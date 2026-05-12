import oyaml as yaml
import sys

def read_docker_compose(file_path, exclude_substrings, cpu_limit, ram_limit):
    with open(file_path, 'r') as file:
        try:
            docker_compose_config = yaml.safe_load(file)
            # print(docker_compose_config)
            if 'services' in docker_compose_config:
                filtered_services = [service for service in docker_compose_config['services'] if not contains_substrings(service, exclude_substrings)]
                for service in filtered_services:
                    if cpu_limit > 0 and ram_limit > 0:
                        if 'deploy' not in docker_compose_config['services'][service]:
                            docker_compose_config['services'][service]['deploy'] = {}
                        if 'resources' not in docker_compose_config['services'][service]['deploy']:
                            docker_compose_config['services'][service]['deploy']['resources'] = {}
                        # docker_compose_config['services'][service]['deploy']['resources']['limits'] = {'cpus': f"{repr(cpu_limit)}", 'memory': f'{ram_limit}G', 'memory-swap': f'{ram_limit}G'}
                        docker_compose_config['services'][service]['deploy']['resources']['limits'] = {'cpus': f"{repr(cpu_limit)}", 'memory': f'{ram_limit}G'}
                        # docker_compose_config['services'][service] = {'memswap_limit': f'{ram_limit}G'}
                        # docker_compose_config['services'][service]['deploy']['resources']['reservations'] = {'memory': f'{ram_limit}G'}
                    
                    if 'secondary' in service or 'primary' in service:
                        
                        # Remove 'labels' section, if present
                        if 'labels' in docker_compose_config['services'][service]:
                            del docker_compose_config['services'][service]['labels']    
                        
                        if 'deploy' not in docker_compose_config['services'][service]:
                            docker_compose_config['services'][service]['deploy'] = {}
                        if 'resources' not in docker_compose_config['services'][service]['deploy']:
                            docker_compose_config['services'][service]['deploy']['resources'] = {}
                            
                        # docker_compose_config['services'][service]['deploy']['resources']['limits'] = {'cpus': f"{repr(cpu_limit)}", 'memory': f'{ram_limit}G', 'memory-swap': f'{ram_limit}G'}
                        # docker_compose_config['services'][service]['deploy']['resources']['limits'] = {'cpus': f"{repr(cpu_limit)}", 'memory': f'{ram_limit}G'}
                        docker_compose_config['services'][service]['deploy']['resources']['limits'] = {'cpus': f"{repr(cpu_limit)}", 'memory': f'{ram_limit}G'}
                        # docker_compose_config['services'][service]['deploy']['resources']['limits'] = {'cpus': "4", 'memory': '8G'}                        
                        # docker_compose_config['services'][service] = {'memswap_limit': f'{ram_limit}G'}
                        # docker_compose_config['services'][service]['deploy']['resources']['reservations'] = {'memory': f'{ram_limit}G'}                                                
                        
                        # Fetching arguments for the Primary initial script
                        if 'primary' in service and 'command' in docker_compose_config['services'][service]:
                            with open('arguments.txt', 'w') as commands_file:
                                commands = ' '.join(docker_compose_config['services'][service]['command'])
                                commands_file.write(commands)                                                                            
                                        
                with open(file_path, 'w') as write_file:
                    yaml.dump(docker_compose_config, write_file, default_flow_style=False)

            else:
                print("The Docker Compose file does not contain the 'services' section.")
        except yaml.YAMLError as e:
            print(f"Error reading the Docker Compose file: {e}")

def contains_substrings(string, substrings):
    return any(substring in string for substring in substrings)

if len(sys.argv) != 3:
    print("Usage: python3 script.py <cpu_limit> <ram_limit>")
    sys.exit(1)

cpu_limit = int(sys.argv[1])
ram_limit = int(sys.argv[2])
# ram_limit = int(ram_limit/3)

file_path = 'topology.yaml'
exclude_substrings = ['bootstrapper', 'god', 'dashboard']
read_docker_compose(file_path, exclude_substrings, cpu_limit, ram_limit)