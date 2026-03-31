import boto3
import time
import os

# Set up Boto3 client for EC2
ec2 = boto3.client('ec2')

# Function to detect server failures
def detect_failures():
    response = ec2.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'stopped':
                print(f"Instance {instance['InstanceId']} is stopped. Provisioning new instance.")
                provision_new_instance()

# Function to provision new instance
def provision_new_instance():
    response = ec2.run_instances(
        ImageId='ami-0c55b159cbfafe1f0',  # Replace with your AMI ID
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',  # Replace with your desired instance type
        KeyName='my-key-pair'  # Replace with your key pair name
    )
    instance_id = response['Instances'][0]['InstanceId']
    print(f"New instance {instance_id} provisioned.")

# Function to monitor real-time traffic and scale instances
def monitor_traffic():
    # Simulate traffic monitoring (replace with actual monitoring logic)
    while True:
        traffic = get_real_time_traffic()  # Replace with your traffic monitoring function
        if traffic > 1000:  # Example threshold for scaling
            scale_instances(1)  # Scale up by 1 instance
        elif traffic < 500:  # Example threshold for scaling down
            scale_instances(-1)  # Scale down by 1 instance
        time.sleep(60)  # Check traffic every 60 seconds

# Function to get real-time traffic (replace with actual implementation)
def get_real_time_traffic():
    # Simulate traffic with random values
    import random
    return random.randint(0, 2000)

# Function to scale instances
def scale_instances(change):
    response = ec2.describe_instances()
    current_instances = len(response['Reservations'])
    new_instances = current_instances + change
    if new_instances > 0:
        for _ in range(abs(change)):
            if change > 0:
                provision_new_instance()
            else:
                terminate_instance()

# Function to terminate instance
def terminate_instance():
    response = ec2.describe_instances()
    instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
    ec2.terminate_instances(InstanceIds=[instance_id])
    print(f"Instance {instance_id} terminated.")

# Main function to run the monitoring system
def main():
    while True:
        detect_failures()
        monitor_traffic()
        time.sleep(300)  # Check for failures every 5 minutes

if __name__ == "__main__":
    main()