import requests
import smtplib
import os
import paramiko
import digitalocean
import time
import schedule


EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
DIGITAL_OCEAN_TOKEN = os.environ.get('DIGITAL_OCEAN_TOKEN')
SERVER_HOST = os.environ.get("SERVER_HOST")
DROPLET_ID = int(os.environ.get("DROPLET_ID"))
SSH_KEY = os.environ.get("SSH_KEY")



def send_notification(email_msg):
    print('Sending an email...')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        message = f"Subject: SITE DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)

def restart_container():
    print('Restarting the application ....')
    ssh = paramiko.SSHClient()
    # for the 1st time when SSHing to host key needs to be accepted/trusted.
    # the below method automatically accepts it.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=SERVER_HOST, username='root',
                key_filename=SSH_KEY)
    # stdin, stdout, stderr = ssh.exec_command('docker ps')
    stdin, stdout, stderr = ssh.exec_command('docker restart 29a3df757b3e')
    print(stdout.readlines())
    ssh.close()

def restart_server_and_container():
    # Restart digital ocean server
    droplet = digitalocean.Droplet(token=DIGITAL_OCEAN_TOKEN,id=DROPLET_ID)
    droplet.load()  # Get current information
    droplet.reboot()
    print("Reboot initiated.")

    # wait for the server to be up before executing docker start command
    while True:
        droplet.load()

        if droplet.status == 'active':
            print("Server is active.")
            # just to be sure after 'active' state, wait 10 seconds and restart container
            time.sleep(10)
            restart_container()
            break

        print("Waiting for server to become active...")
        time.sleep(5)

def monitor_application():
    print('Monitoring application ....', flush=True)

    try:
        # change the IP address in the below command to match the monitored server
        response = requests.get(f'http://{SERVER_HOST}:8080',timeout=10)
        print(response.status_code)

        if response.status_code == 403:
           print('Application is running successfully!')
        else:
            print('Application Down. Fix it!')
            msg = f'Application returned {response.status_code}'
            send_notification(msg)
            restart_container()

    except Exception as ex:
        print(f'Connection error happened: {ex}')
        msg = 'Server unreachable'
        send_notification(msg)
        restart_server_and_container()

# start of main code
schedule.every(1).minutes.do(monitor_application)

# run script immediately once
monitor_application()

while True:
    schedule.run_pending()
    # sleeps for 1 second then executes the code in while loop (schedule.run)
    time.sleep(1)







