"""
Paco References
"""

from paco.models import vocabulary, schemas
from paco.models.locations import get_parent_by_interface
from paco.models.exceptions import InvalidPacoReference
from ruamel.yaml.compat import StringIO
from operator import itemgetter
import importlib
import pathlib
import ruamel.yaml
import os


ami_cache = {}
g_outputs_dict_cache = {}
g_outputs_dict_cache_time = {}

class YAML(ruamel.yaml.YAML):
    def dump(self, data, stream=None, **kw):
        dumps = False
        if stream is None:
            dumps = True
            stream = StringIO()
        ruamel.yaml.YAML.dump(self, data, stream, **kw)
        if dumps:
            return stream.getvalue()

# ToDo: this is duplicated between reftypes and references
import zope.schema
class InvalidPacoReferenceString(zope.schema.ValidationError):
    __doc__ = 'PacoReference must be of type (string)'

class InvalidPacoReferenceStartsWith(zope.schema.ValidationError):
    __doc__ = "PacoReference must begin with 'paco.ref'"

class InvalidPacoReferenceRefType(zope.schema.ValidationError):
    __doc__ = "PacoReference 'paco.ref must begin with: netenv | resource | accounts | function | service"

def is_ref(paco_ref, raise_enabled=False):
    """Determines if the string value is a Paco reference"""
    if type(paco_ref) != type(str()):
        if raise_enabled: raise InvalidPacoReferenceString
        return False
    if paco_ref.startswith('paco.ref ') == False:
        if raise_enabled: raise InvalidPacoReferenceStartsWith
        return False
    ref_types = ["netenv", "resource", "accounts", "function", "service", "alias"]
    for ref_type in ref_types:
        if paco_ref.startswith('paco.ref %s.' % ref_type):
            return True
    if raise_enabled: raise InvalidPacoReferenceRefType
    return False

class Reference():
    """
    Reference to something in the paco.models

    attributes:
      raw : original reference str : 'paco.ref netenv.pacodemo.network.vpc.security_groups.app.lb'
      type : reference type str : 'netenv'
      parts : list of ref parts : ['netenv', 'pacodemo', 'network', 'vpc', 'security_groups', 'app', 'lb']
      ref : reffered string : 'netenv.pacodemo.network.vpc.security_groups.app.lb'
    """

    def __init__(self, value):
        self.raw = value
        self.ref = value.split(' ', 2)[1]
        self.parts = self.ref.split('.')
        self.type = self.parts[0]
        # resource_ref is the tail end of the reference that is
        # relevant to the Resource it references
        self.resource = None
        self.resource_ref = None
        self.region = None

        if self.type == 'netenv' or self.type == 'service':
            # paco.ref service.describe.<account>.<region>.myapp
            # pace.ref netenv.dev.<account>.<region>.applications
            # do not try to find region for short environment refs like 'paco.ref netenv.mynet.prod'
            if len(self.parts) > 3:
                if self.parts[3] in vocabulary.aws_regions.keys():
                    self.region = self.parts[3]
        elif self.type == 'resource':
            if self.parts[1] == 'cloudwatch' and len(self.parts) >= 4:
                self.region = self.parts[4]

        if is_ref(self.raw) == False:
            print("Invalid Paco reference: %s" % (value))

    def get_object(self, project):
        return get_model_obj_from_ref(self.raw, project)

    def get_netenv_app_name(self):
        try:
            app_idx = self.parts.index('applications')
        except ValueError:
            return None
        return self.parts[app_idx+1]

    def get_netenv_env_name(self):
        try:
            netenv_idx = self.parts.index('netenv')
        except ValueError:
            return None

        if self.parts[netenv_idx+2] == 'applications':
            return None
        return self.parts[netenv_idx+2]

    def set_netenv_app_name(self, new_app_name):
        try:
            app_idx = self.parts.index('applications')
        except Exception as e:
            return None
        match_str = f'applications.{self.parts[app_idx+1]}.'
        replace_str = f'applications.{new_app_name}.'
        self.raw = self.raw.replace(match_str, replace_str)
        self.ref = self.ref.replace(match_str, replace_str)
        self.parts[app_idx+1] = new_app_name

    def get_environment_name(self, project):
        environment_name = None
        if len(self.parts) > 2:
            environment_name = self.parts[2]
        return environment_name

    def get_account(self, project, resource = None):
        "Account object this reference belongs to"
        if self.type == 'service':
            return project.accounts[self.parts[2]]
        elif self.type == 'netenv':
            if resource == None:
                resource = self.get_model_obj(project)
            env_reg = get_parent_by_interface(resource, schemas.IEnvironmentRegion)
            return get_model_obj_from_ref(env_reg.network.aws_account, project)
        elif self.type == 'accounts':
            return project.accounts[self.parts[1]]
        elif self.type == 'resource':
            if self.ref.startswith('resource.cloudwatch'):
                return self.parts[3]
        return None

    def gen_name(self, project):
        app_name = 'unkown'
        group_name = 'unknown'
        res_name = 'unknown'
        if self.parts[0] == 'netenv':
            netenv_name = self.parts[1]
            # if part[3] is a region, we know the previous part is the environment
            if self.parts[3] in vocabulary.aws_region_names:
                env_name = self.parts[2]
                if self.parts[4] == 'applications':
                    app_name = self.parts[5]
                    group_name = self.parts[7]
                    res_name = self.parts[9]
            elif self.parts[2] == 'applications':
                app_name = self.parts[3]
                group_name = self.parts[5]
                res_name = self.parts[7]
            name = f'{netenv_name}-{env_name}-{app_name}-{group_name}-{res_name}'
        else:
            name = 'unknown'

        return name

    @property
    def last_part(self):
        return self.parts[-1]

    def next_part(self, search_ref):
        search_parts = search_ref.split('.')
        first_found = False
        for ref_part in self.parts:
            if first_found == True:
                if search_idx == len(search_parts):
                    return ref_part
                elif ref_part == search_parts[search_idx]:
                    search_idx += 1
            elif ref_part == search_parts[0]:
                first_found = True
                search_idx = 1

        return None

    def sub_part(self, part, value):
        self.raw = self.raw.replace(part, value)
        self.ref = self.ref.replace(part, value)
        self.parts = self.ref.split('.')

    def set_account_name(self, account_name):
        self.sub_part('<account>', account_name)

    def set_environment_name(self, environment_name):
        self.sub_part('<environment>', environment_name)

    def set_region(self, region):
        self.region = region
        self.sub_part('<region>', region)

    def resolve(self, project, account_ctx=None, resolve_from_outputs=False):
        return resolve_ref(
            ref_str=None,
            project=project,
            account_ctx=account_ctx,
            ref=self,
            resolve_from_outputs=resolve_from_outputs
        )

    def get_model_obj(self, project):
        return get_model_obj_from_ref(self, project)

    def secret_base_ref(self):
        """
Secret Manager Secrets can be a ref to the Secret:

  paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb

Or they can be a ref to a JSON field within the Secret value:

  paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb.myjsonfield

Either ref type can also specify the ARN of the Secret:

  paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb.arn
  paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.mydb.myjsonfield.arn

Return only the base ref and strip the final part that specifies the JSON Field from the ref.
For all of the above examples, this would return:

  paco.ref netenv.mynet.secrets_manager.myapp.mygroup.mydb

        """
        new_ref_obj = self
        if self.type == 'netenv':
            # remove final .arn but allow for a secret named 'arn'
            #   paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.arn
            #   paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.arn.arn
            #   paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.arn.myjson
            #   paco.ref netenv.mynet.dev.eu-central-1.secrets_manager.myapp.mygroup.arn.myjson.arn
            if len(self.parts) == 7:
                pass
            elif len(self.parts) > 7:
                new_ref = self.parts[:8]
                new_ref = '.'.join(new_ref)
                new_ref_obj = Reference(f'paco.ref {new_ref}')
            else:
                raise InvalidPacoReference("Not a valid Secret ref")
        elif self.type == 'service':
            # service.notification.secrets_manager.myapp.mygroup.mysecret
            if len(self.parts) > 5:
                new_ref = self.parts[:6]
                new_ref = '.'.join(new_ref)
                new_ref_obj = Reference(f'paco.ref {new_ref}')
            else:
                raise InvalidPacoReference("Not a valid Secret ref")
        else:
            raise NotImplemented('What kind of Secret do you have?!?')
        return new_ref_obj

def get_model_obj_from_ref(ref, project, referring_obj=None):
    """Resolves the reference to the model object it refers to.
    ref can be either a string or a Reference object.
    """
    if isinstance(ref, str):
        ref = Reference(ref)
    obj = project
    for part_idx in range(0, len(ref.parts)):
        # special case for resource.route53 hosted zone look-ups
        if schemas.IRoute53Resource.providedBy(obj):
            if len(ref.parts) == 3:
                if ref.parts[2] == 'hosted_zones':
                    return obj
                else:
                    return obj.hosted_zones[ref.parts[2]]
            else:
                return obj
        try:
            next_obj = obj[ref.parts[part_idx]]
        except (TypeError, KeyError):
            next_obj = getattr(obj, ref.parts[part_idx], None)
        if next_obj != None and isinstance(next_obj, str) == False:
            obj = next_obj
        else:
            message = f"\nCould not find model at {ref.raw}\n"
            message += f"\nLook-up reached: {obj.paco_ref_parts}\n"
            message += f"\nCould not find next part: {ref.parts[part_idx]}\n"
            if referring_obj != None:
                message += f"Object: {referring_obj.paco_ref_parts}\n"
            if ref.parts[0] in ['iam', 'codecommit', 'ec2', 'sns', 's3', 'route53', 'resources']:
                message += "Did you mean to run:\n"
                message += "paco <command> resource.{}?\n".format(ref.ref)
            raise InvalidPacoReference(message)

    return obj

def get_resolve_ref_obj(project, obj, ref, part_idx_start, resolve_from_outputs=False):
    """
    Traverses the reference parts looking for the last child that
    is a not a string. This object is expected to be a part of the
    model and should have a resolve_ref method that can be called.
    """
    for part_idx in range(part_idx_start, len(ref.parts)):
        # the model can be walked with either obj[name] or obj.name
        # depending on what is being walked
        name = ref.parts[part_idx]
        try:
            next_obj = obj[name]
        except (TypeError, KeyError):
            next_obj = getattr(obj, name, None)
        if next_obj != None and isinstance(next_obj, str) == False and isinstance(next_obj, int) == False:
            obj = next_obj
        else:
            # Given a ref of 'netenv.websites.prod.[...].resources.database.endpoint.address' then
            # after walks to the RDS Resource named '.database' it won't be able to find the next '.endpoint'
            # and will break here
            break

    ref.resource_ref = '.'.join(ref.parts[part_idx:])
    ref.resource = obj
    if resolve_from_outputs == True:
        outputs_value = resolve_ref_outputs(ref, project['home'])
        if outputs_value != None:
            return outputs_value

    try:
        response = obj.resolve_ref(ref)
    except AttributeError:
        # Check if we have something stored in Outputs
        outputs_value = resolve_ref_outputs(ref, project['home'])
        if outputs_value != None:
            return outputs_value
        raise_invalid_reference(ref, obj, ref.parts[part_idx:][0])
    return response

def resolve_ref_outputs(ref, project_home_path):
    global g_outputs_dict_cache
    global g_outputs_dict_cache_time
    key = ref.parts[0]
    # ToDo: .paco-work is part of paco not paco.models, refactor?
    output_filepath = pathlib.Path(project_home_path) / '.paco-work' / 'outputs' / key
    output_filepath = output_filepath.with_suffix('.yaml')
    if output_filepath.exists() == False:
        return None

    yaml = YAML(typ="safe", pure=True)
    yaml.default_flow_sytle = False

    # Caching the outputs file increases performance signficantly
    outputs_file_last_modified = os.path.getmtime(output_filepath)
    cache_type = ref.parts[0]
    if cache_type not in g_outputs_dict_cache_time.keys():
        g_outputs_dict_cache_time[cache_type] = 0

    if outputs_file_last_modified > g_outputs_dict_cache_time[cache_type]:
        g_outputs_dict_cache_time[cache_type] = outputs_file_last_modified
        with open(output_filepath, "r") as output_fd:
            g_outputs_dict_cache[cache_type] = yaml.load(output_fd)


    outputs_dict = g_outputs_dict_cache[cache_type]
    for part in ref.parts:
        if part not in outputs_dict.keys():
            break
        node = outputs_dict[part]
        outputs_dict = node
        if node == None:
            break

        if len(list(node.keys())) == 1 and '__name__' in node.keys():
            return node['__name__']

    return None

def raise_invalid_reference(ref, obj, name):
    """Takes the ref attempting to be looked-up,
    an obj that was the last model traversed too,
    the name that failed the next look-up.
    """
    raise InvalidPacoReference("""
Reference: {}

Reference look-up failed at '{}' trying to find name '{}'.
""".format(ref.raw, obj.paco_ref_parts, name))

def resolve_ref(ref_str, project, account_ctx=None, ref=None, resolve_from_outputs=False):
    """Resolve a reference"""
    if ref == None:
        ref = Reference(ref_str)
    ref_value = None
    if ref.type == "resource":
        try:
            if ref.ref.startswith('resource.iam.identity_providers'):
                return get_resolve_ref_obj(project, project, ref, part_idx_start=0, resolve_from_outputs=resolve_from_outputs)
            elif ref.ref.startswith('resource.ec2.eips'):
                return get_resolve_ref_obj(project, project, ref, part_idx_start=0, resolve_from_outputs=resolve_from_outputs)
            if ref.ref.startswith('resource.iam.policies'):
                return get_resolve_ref_obj(project, project, ref, part_idx_start=0, resolve_from_outputs=resolve_from_outputs)
            else:
                resource_obj = project['resource'][ref.parts[1]]
                ref_value = resource_obj.resolve_ref(ref)
        except KeyError:
            raise_invalid_reference(ref, project['resource'], ref.parts[1])
    elif ref.type == "service":
        #resolve_from_outputs=True
        return get_resolve_ref_obj(project, project, ref, part_idx_start=0, resolve_from_outputs=resolve_from_outputs)
    elif ref.type == "netenv":
        try:
            obj = project['netenv']
            for i in range(1,4):
                obj = obj[ref.parts[i]]
        except KeyError:
            raise_invalid_reference(ref, obj, ref.parts[i])
        return get_resolve_ref_obj(project, obj, ref, 4, resolve_from_outputs)

    elif ref.type == "accounts":
        ref_value = resolve_accounts_ref(ref, project)
    elif ref.type == "function":
        ref_value = resolve_function_ref(ref, project, account_ctx)
    else:
        raise ValueError(f"Unsupported ref type: {ref.raw}: {ref.type}")

    if resolve_from_outputs == True:
        outputs_value = resolve_ref_outputs(ref, project['home'])
        if outputs_value != None:
            ref_value = outputs_value

    return ref_value

def function_ec2_ami_latest(ref, project, account_ctx):
    """EC2 AMI latest"""
    ami_description = None
    ami_name = None
    owner_alias = "amazon"
    ami_owner = "amazon"
    ami_architecture = 'x86_64'
    product_code_type = 'aws'
    filter_type = 'aws'
    owner_id = "*"
    if ref.last_part == 'amazon-linux-2':
        ami_description = "Amazon Linux 2 AMI*"
        ami_name = 'amzn2-ami-hvm-*'
    elif ref.last_part == 'amazon-linux':
        ami_description = "Amazon Linux AMI*"
        ami_name = 'amzn-ami-hvm-*'
    elif ref.last_part == 'amazon-linux-nat':
        ami_description = "Amazon Linux AMI*"
        ami_name = 'amzn-ami-vpc-nat-*'
    elif ref.last_part == 'amazon-linux-2-ecs':
        ami_description = "Amazon Linux AMI*"
        ami_name = "amzn2-ami-ecs-hvm-*"
    elif ref.last_part == 'amazon-linux-2-ecs-arm64':
        ami_description = "Amazon Linux AMI*"
        ami_name = "amzn2-ami-ecs-hvm-*"
        ami_architecture = 'arm64'
    elif ref.last_part == 'amazon-linux-2023-ecs':
        ami_description = "Amazon Linux AMI 2023*"
        ami_name = "al2023-ami-ecs-hvm-2023.*"
        ami_owner = '591542846629'
        ami_architecture = 'x86_64'
    elif ref.last_part == 'ubuntu-18':
        ami_name = "ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"
        ami_owner = "099720109477"
        filter_type = "ubuntu"
    elif ref.last_part == 'ubuntu-20':
        ami_name = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
        ami_owner = "099720109477"
        filter_type = "ubuntu"
    elif ref.last_part == 'ubuntu-22':
        ami_name = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
        ami_owner = "099720109477"
        filter_type = "ubuntu"
    elif ref.last_part == 'ubuntu-22-arm':
        ami_name = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-arm64-server-*"
        ami_owner = "099720109477"
        filter_type = "ubuntu"
        ami_architecture = 'arm64'
    elif ref.last_part == 'ubuntu-20-arm':
        ami_name = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-arm64-server-*"
        ami_owner = "099720109477"
        filter_type = "ubuntu"
        ami_architecture = 'arm64'


    elif ref.last_part == 'cis-ubuntu-18-level-1':
        ami_description = "CIS Ubuntu Linux 18.04 LTS Benchmark*"
        ami_name = "CIS Ubuntu Linux 18.04 LTS Benchmark*"
        ami_owner = 'aws-marketplace'
        owner_alias = 'aws-marketplace'
        product_code_type = 'marketplace'
        product_code = 'b1e35cepur7ecue1bq883thxr'
        filter_type = 'aws_marketplace'
    else:
        raise ValueError("Unsupported AMI Name: {}".format(ref.last_part))

    cache_id = ref.last_part
    if cache_id in ami_cache.keys():
        return ami_cache[cache_id]

    ec2_client = account_ctx.get_aws_client('ec2', aws_region=ref.region)
    common_filters = [
            {
                'Name': 'name',
                'Values': [ami_name]
            },{
                'Name': 'state',
                'Values': ['available']
            },{
                'Name': 'virtualization-type',
                'Values': ['hvm']
            },{
                'Name': 'architecture',
                'Values': [ami_architecture]
            }
    ]
    filters = common_filters
    if filter_type == 'aws':
        filters.extend([
            {
                'Name': 'description',
                'Values': [ami_description]
            },
            {
                'Name': 'owner-alias',
                'Values': [owner_alias]
            },{
                'Name': 'owner-id',
                'Values': [owner_id]
            },{
                'Name': 'root-device-type',
                'Values': ['ebs']
            },{
                'Name': 'hypervisor',
                'Values': ['xen']
            },{
                'Name': 'image-type',
                'Values': ['machine']
            }
        ])
    elif filter_type == 'aws_marketplace':
        filters.extend([
            {
                'Name': 'product-code.type',
                'Values': [product_code_type]
            },{
                'Name': 'product-code',
                'Values': [product_code]
            }
        ])

    ami_list= ec2_client.describe_images(
        Filters=filters,
        Owners=[
            ami_owner
        ]
    )
    # TODO: Handle empty list
    if len(ami_list['Images']) == 0:
        breakpoint()
        return

    # Sort on Creation date Desc
    image_details = sorted(ami_list['Images'],key=itemgetter('CreationDate'),reverse=True)
    # TODO: Also check if the latest image is out of date: > X days old?
    ami_id = image_details[0]['ImageId']
    ami_cache[cache_id] = ami_id
    return ami_id

def import_and_call_function(ref, project, account_ctx):
    "Import a module and call a function in it with the Reference, Project and AccountContext"
    module_name = '.'.join(ref.parts[1:-1])
    if module_name.find(':') != -1:
        module_name = module_name.split(':')[0]
        function_name = module_name.split('.')[-1:][0]
        module_name = '.'.join(module_name.split('.')[:-1])
        module = importlib.import_module(module_name)
        extra_context = ref.raw.split(':')[1]
        return getattr(module, function_name)(ref, extra_context, project, account_ctx)
    else:
        function_name = ref.parts[-1:][0]
        module = importlib.import_module(module_name)
        return getattr(module, function_name)(ref, project, account_ctx)

def resolve_function_ref(ref, project, account_ctx):
    if account_ctx == None:
        return None
    if ref.ref.startswith('function.aws.ec2.ami.latest'):
        # ToDo: call this as a proper function ref? migrate it?
        return function_ec2_ami_latest(ref, project, account_ctx)
    else:
        return import_and_call_function(ref, project, account_ctx)

def resolve_accounts_ref(ref, project):
    "Return an IAccount object from the model."
    try:
        account = project[ref.parts[0]][ref.parts[1]]
    except KeyError:
        raise InvalidPacoReference("Can not resolve the reference '{}'".format(ref.raw))

    return account.resolve_ref(ref)

