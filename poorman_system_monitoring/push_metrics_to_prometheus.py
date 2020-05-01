import asyncio
import csv
import logging
import os

import aiohttp

MEMORY_COMMAND = 'head -n 1 /proc/meminfo | awk \'{print $2}\''
PROCESS_INFORMATION = 'ps -o pid,uid,%mem,command ax'
SSH_COMMAND_TO_RETRIEVE = "ssh " \
                          "-o UserKnownHostsFile=/dev/null " \
                          "-o StrictHostKeyChecking=no " \
                          "-i %s %s@%s "
PUSHGATEWAY_URL = os.getenv('PUSHGATEWAY_URL', 'http://localhost:9091')


async def memory_retrieval(params):
    command = base_ssh_command(params)
    logging.info(f"Getting information from host: {params['host']}")
    memory_process = await asyncio.create_subprocess_shell(
        f"{command} {MEMORY_COMMAND}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    memory_stdout, memory_stderr = await memory_process.communicate()
    current_server_memory = -1
    if memory_stdout:
        current_server_memory = int(memory_stdout.decode())
    logging.info(f"Server: {params['host']}, Memory: {current_server_memory}")
    return current_server_memory


def base_ssh_command(params):
    return SSH_COMMAND_TO_RETRIEVE % (params['key_location'], params['user'], params['host'])


def escape_label_chars(param: str):
    return param \
        .replace("\\", "\\\\") \
        .replace("\n", "\\n") \
        .replace("\"", "\\""")


def camelize_string(param: str):
    return param \
        .replace("\\", "_") \
        .replace(" ", "_") \
        .replace(":", "_") \
        .replace("-", "_") \
        .replace("[", "_") \
        .replace("]", "_") \
        .replace("/", "_") \
        .replace("=", "_") \
        .replace("(", "") \
        .replace(")", "")


def parse_to_open_metrics_format(host_information, columns, current_server_memory):
    return f'''
# TYPE process_{camelize_string(columns[3])}_id gauge
process_{camelize_string(columns[3])}_id{{instance=\"{host_information['host']}\",command=\"{escape_label_chars(
        " ".join(columns[3:]))}\"}} {int(columns[0])}
# TYPE process_{camelize_string(columns[3])}_uid gauge
process_{camelize_string(columns[3])}_uid{{instance=\"{host_information['host']}\"}} {columns[1]}
# TYPE total_memory gauge
total_memory{{instance=\"{host_information['host']}\"}} {current_server_memory}
# TYPE process_{camelize_string(columns[3])}_memory_percentage gauge
process_{camelize_string(columns[3])}_memory_percentage{{instance=\"{host_information['host']}\"}} {float(
        columns[2])}
# TYPE process_{camelize_string(columns[3])}_memory_usage gauge
process_{camelize_string(columns[3])}_memory_usage{{instance=\"{host_information[
        'host']}\"}} {current_server_memory * float(
        columns[2]) / 100}
'''


async def processes_information(host_information, current_server_memory):
    logging.info(f"Getting processes information from host: {host_information['host']}")
    ps_process = await asyncio.create_subprocess_shell(
        f"{base_ssh_command(host_information)} {PROCESS_INFORMATION}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    process_list = []
    ps_process_stdout, ps_process_stderr = await ps_process.communicate()

    logging.info("Transforming result into OpenMetrics standard")
    if ps_process_stdout:
        lines = ps_process_stdout.decode().splitlines()
        for i in range(1, len(lines)):
            columns = lines[i].split()
            result = parse_to_open_metrics_format(host_information, columns, current_server_memory)
            process_list.append(result)
            logging.info(result)
    logging.info(process_list)
    logging.info("Finished parsing information from host")
    return process_list


async def push_to_prometheus(host_info, list_processes):
    host = f"{PUSHGATEWAY_URL}/metrics/job/metrics_collection/instance/{host_info['host']}"
    logging.info(f"Pushing information to prometheus push gateway: {host}")
    results = []
    for process_info in list_processes:
        async with aiohttp.ClientSession(headers={'Content-Type': 'text/plain'}).post(host, data=process_info) as resp:
            response_text = await resp.text()
            response_code = resp.status
            logging.info(process_info)
            formatted_response = f"{response_code} - {response_text} - \n {process_info}"
            logging.info(f"Result from request: \n host: {host}, \n response: {formatted_response}")
            results.append(formatted_response)
            resp.close()
    return results


async def main():
    server_list = []
    logging.info("Reading hosts inventory from csv")
    with open("./servers_inventory.csv", "+r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            server_list.append(row)
    logging.info("Getting memory information from each server")
    memory_results = [asyncio.ensure_future(memory_retrieval(values)) for values in server_list]
    await asyncio.wait(memory_results)
    logging.info("Getting information per process from each server")
    processes_results = [asyncio.ensure_future(processes_information(server_list[i], memory_results[i].result())) for i
                         in
                         range(0, len(server_list))]
    await asyncio.wait(processes_results)
    logging.info("Pushing information to prometheus")
    prometheus_push_results = [
        asyncio.ensure_future(
            push_to_prometheus(server_list[i], processes_results[i].result())
        ) for i in range(0, len(processes_results))]
    await asyncio.wait(prometheus_push_results)
    logging.info("Finished sending information to prometheus")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
