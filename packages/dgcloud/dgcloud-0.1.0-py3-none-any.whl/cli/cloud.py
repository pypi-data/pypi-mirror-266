import paramiko

class ServerManager:
    def __init__(self, server_ip, ssh_user, ssh_password):
        self.server_ip = server_ip
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        
    def ssh_execute_command(self, command, port=22):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(self.server_ip, port=port, username=self.ssh_user, password=self.ssh_password)

        stdin, stdout, stderr = ssh.exec_command(command)
        stdout = stdout.read().decode()
        stderr = stderr.read().decode()
        ssh.close()
        return stdout,stderr


    def git_pull(self, git_repo_path):
        command = f'cd {git_repo_path} && git pull'
        return self.ssh_execute_command(command)
    
    def git_application_status(self):
        command = "sudo systemctl status {applicaiton_socket} | grep 'Active' "
        status_data,stderr = self.ssh_execute_command(command)
        status = status_data.strip().split("since")[0].split("Active: ")[-1]
        return status