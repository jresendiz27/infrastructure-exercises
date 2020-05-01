import asyncio
import requests
import aiohttp
import csv

MEMORY_COMMAND = 'head -n 1 /proc/meminfo | awk \'{print $2}\''
PROCESS_INFORMATION = 'ps -o pid,uid,%mem,command ax'
# PROCESS_INFORMATION = 'ps -eo pid,user,vsize,cmd'
SSH_COMMAND_TO_RETRIEVE = "ssh " \
                          "-o UserKnownHostsFile=/dev/null " \
                          "-o StrictHostKeyChecking=no " \
                          "-i %s %s@%s "


async def memory_retrieval(params):
    command = base_ssh_command(params)
    memory_process = await asyncio.create_subprocess_shell(
        f"{command} {MEMORY_COMMAND}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    memory_stdout, memory_stderr = await memory_process.communicate()
    current_server_memory = -1
    if memory_stdout:
        current_server_memory = int(memory_stdout.decode())
    return current_server_memory


def base_ssh_command(params):
    return SSH_COMMAND_TO_RETRIEVE % (params['key_location'], params['user'], params['host'])


async def processes_information(params, current_server_memory):
    ps_process = await asyncio.create_subprocess_shell(
        f"{base_ssh_command(params)} {PROCESS_INFORMATION}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    process_list = []
    ps_process_stdout, ps_process_stderr = await ps_process.communicate()
    if ps_process_stdout:
        lines = ps_process_stdout.decode().splitlines()
        for i in range(1, len(lines)):
            columns = lines[i].split()
            # command {" ".join(columns[3:])}
            result = f'''
process_id {int(columns[0])}
# TYPE process_owner untyped
process_owner '{columns[1]}'
process_memory_percentage {float(columns[2])}
process_memory_usage {current_server_memory * float(columns[2]) / 100}
'''

            process_list.append(result)
    return process_list


async def push_to_prometheus(host_info, list_processes):
    # aqui la wea del push
    host = f"http://localhost:9091/metrics/job/{host_info}"
    results = []
    for process in list_processes:
        print(process)
        async with aiohttp.ClientSession(headers={'Content-Type': 'text/plain'}).post(host, data=process) as resp:
            print(f"{await resp.text()}")
            results.append(f"{resp.text()} - {resp.status}")

    return results


async def main():
    server_list = []
    with open("./servers_inventory.csv", "+r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            server_list.append(row)

    memory_results = [asyncio.ensure_future(memory_retrieval(values)) for values in server_list]
    await asyncio.wait(memory_results)

    processes_results = [asyncio.ensure_future(processes_information(server_list[i], memory_results[i].result())) for i
                         in
                         range(0, len(server_list))]
    await asyncio.wait(processes_results)

    prometheus_push_results = [
        asyncio.ensure_future(
            push_to_prometheus(f"{server_list[i]['host']}-{i}", processes_results[i].result())
        ) for i in range(0, len(processes_results))]

    await asyncio.wait(prometheus_push_results)
    print("Hola")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
