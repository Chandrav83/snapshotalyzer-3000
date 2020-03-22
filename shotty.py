import boto3
import click

session = boto3.Session(profile_name='cprofile')
ec2 = session.resource('ec2')

""" Function to list the instances """
def filter_instances(project):
    instances = []
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

""" Start of click group """
@click.group()
def cli():

    """ this lists the snapshots """
@cli.group('snapshots')
def snapshots():
    """ Commands for snapshots """
@snapshots.command('list')
@click.option('--project', default=None,
    help="Only Snapshots for project (tag Project:<name>)")
def list_snapshots(project):
    "List EC2 snapshots"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))
    return

""" this lists the volumes """
@cli.group('volumes')
def volumes():
    """ Commands for volumes """
@volumes.command('list')
@click.option('--project', default=None,
help="Only Volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return

""" start of list instances """
@cli.group('instances')
def instances():

    """Commands for Instances"""
@instances.command('snapshot',
    help="Create snapshots for all volumes")
@click.option('--project', default=None,
help="Only instances for project (tag Project:<name>)")
def create_snapshot(project):
    """ Create snapshots of the volumes of EC2 instances """
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by SnapshotAlyzer")
    return

    
@instances.command('list')
@click.option('--project', default=None,
help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
        i.id,
        i.instance_type,
        i.placement['AvailabilityZone'],
        i.state['Name'],
        i.public_dns_name,
        tags.get('Project', '<no project>'))))
    return

""" To Stop an Instances """
@instances.command('stop')
@click.option('--project', default=None,
help="Only instances for project (tag Project:<name>)")
def stop_instances(project):
    "Stop EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
    return

""" To Start an Instances """
@instances.command('start')
@click.option('--project', default=None,
help="Only instances for project (tag Project:<name>)")
def start_instances(project):
    "Starting EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        i.start()
    return

""" Program execution begins here """
if __name__ == '__main__':
    cli()
