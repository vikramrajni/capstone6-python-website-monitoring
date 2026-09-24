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


response = requests.get('http://x.x.x.x:8080')
print(response.status_code)

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
    ssh.connect(hostname='x.x.x.x', username='root',
                key_filename=r"C:\path to private key file")
    # stdin, stdout, stderr = ssh.exec_command('docker ps')
    stdin, stdout, stderr = ssh.exec_command('docker start 6edc47c8bdb0')
    print(stdout.readlines())
    ssh.close()

def restart_server_and_container():
    # Restart digital ocean server
    droplet = digitalocean.Droplet(token=DIGITAL_OCEAN_TOKEN,id=xxxxxxx)
    droplet.load()  # Get current information
    droplet.reboot()
    print("Reboot initiated.")

    # wait for the server to be up before executing docker start command
    while True:
        Jenkins_server = droplet.load()
        if Jenkins_server.status == 'active':
            # just to be sure after 'active' state, wait 10 seconds and start container
            time.sleep(10)
            restart_container()
            break

def monitor_application():
    print('Monitoring application ....')

    try:
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

schedule.every(5).minutes.do(monitor_application)
while True:
    schedule.run_pending()







