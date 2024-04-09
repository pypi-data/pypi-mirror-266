from paco.models import schemas, vocabulary
from paco.models.base import Deployable, Parent, Named, Name, Resource, ApplicationResource, AccountRef, Regionalized, get_all_fields
from paco.models.formatter import get_formatted_model_context
from paco.models.logging import CloudWatchLogSets
from paco.models.locations import get_parent_by_interface
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
import json
import paco.models.exceptions
import paco.models.services
import paco.models.registry
import troposphere
import troposphere.cloudwatch


class Monitor(Named, dict):
    pass

@implementer(schemas.ISNSTopics)
class SNSTopics(AccountRef, Named, dict):
    "Container for SNS Topics"
    regions = FieldProperty(schemas.ISNSTopics["regions"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.regions = ['ALL']

    def resolve_ref(self, ref):
        return self.resolve_ref_obj.resolve_ref(ref)

@implementer(schemas.IHealthChecks)
class HealthChecks(Named, dict):
    pass

@implementer(schemas.IAlarmNotifications)
class AlarmNotifications(Named, dict):
    "Container of AlarmNotifications"

    def to_dict(self):
        export_dict = {}
        # Notify Sections
        for notify_key in self.keys():
            notify = self[notify_key]
            export_dict[notify_key] = {}
            for field_name in get_all_fields(notify).keys():
                field_obj = getattr(notify, field_name)
                if field_obj != None:
                    export_dict[notify_key][field_name] = field_obj


        return export_dict

@implementer(schemas.IAlarmNotification)
class AlarmNotification(Named):
    "AlarmNotification"
    groups = FieldProperty(schemas.IAlarmNotification["groups"])
    classification = FieldProperty(schemas.IAlarmNotification["classification"])
    severity = FieldProperty(schemas.IAlarmNotification["severity"])

@implementer(schemas.IAlarmSet)
class AlarmSet(Named, dict):
    resource_type = FieldProperty(schemas.IAlarmSet["resource_type"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.notifications = AlarmNotifications('notifications', self)

@implementer(schemas.IAlarmSets)
class AlarmSets(Named, dict):
    "Collection of Alarms"

class AlarmSetsContainer(Named, dict):
    "Collection of AlarmSets"

@implementer(schemas.IAlarm)
class Alarm(Named, Regionalized, Deployable):
    "Alarm"
    classification = FieldProperty(schemas.IAlarm["classification"])
    description = FieldProperty(schemas.IAlarm["description"])
    runbook_url = FieldProperty(schemas.IAlarm["runbook_url"])
    severity = FieldProperty(schemas.IAlarm["severity"])

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.notifications = AlarmNotifications('notifications', self)
        self.enabled = True

    def _add_notifications_to_groups(self, notifications, groups):
        for notification in notifications.values():
            # do not add if it is filtered out
            if notification.classification and self.classification != notification.classification:
                continue
            if notification.severity and self.severity != notification.severity:
                continue
            for group in notification.groups:
                if group not in groups:
                    groups[group] = None
        return groups

    @property
    def notification_groups(self):
        "A unique list of notification groups that an Alarm is subscribed to"
        groups = {}
        notification_config = self.get_notifications_config(match_with_alarm=True)
        if notification_config != None:
            return notification_config.groups

        return []



    def get_alarm_actions_paco_refs(self, snstopics=None):
        """Return a list of alarm actions in the form of paco.ref SNS Topic ARNs, e.g.

        'paco.ref service.notification.applications.notification.groups.lambda.resources.snstopic.arn'

        This will by default be a list of SNS Topics that the alarm is subscribed to.
        However, if a plugin is registered, it will provide the actions instead.
        """
        # if a Service has registered a custom AlarmActions hook, call that instead
        if paco.models.registry.CW_ALARM_ACTIONS_HOOK != None:
            return paco.models.registry.CW_ALARM_ACTIONS_HOOK(self)

        # default behaviour is to use notification groups directly
        if snstopics == None:
            return None
        notification_arns = [
            snstopics[group].paco_ref + '.arn' for group in self.notification_groups
        ]
        if len(notification_arns) > 5:
            raise paco.models.exceptions.InvalidPacoProjectFile("""
    Alarm {} has {} actions, but CloudWatch Alarms allow a maximum of 5 actions.

    {}""".format(self.name, len(notification_arns), get_formatted_model_context(self))
            )

        return notification_arns

    @property
    def actions_enabled(self):
        if hasattr(self, 'alarm_actions'):
            if len(self.alarm_actions) > 0:
                return True
        return None

@implementer(schemas.IDimension)
class Dimension(Parent):
    name = FieldProperty(schemas.IDimension["name"])
    value = FieldProperty(schemas.IDimension["value"])

    def __init__(self, __parent__, name='', value=''):
        self.__parent__ = __parent__
        self.name = name
        self.value = value

@implementer(schemas.ISimpleCloudWatchAlarm)
class SimpleCloudWatchAlarm(Parent):
    "CloudWatch Alarm"
    alarm_description = FieldProperty(schemas.ISimpleCloudWatchAlarm["alarm_description"])
    actions_enabled = FieldProperty(schemas.ISimpleCloudWatchAlarm["actions_enabled"])
    metric_name = FieldProperty(schemas.ISimpleCloudWatchAlarm["metric_name"])
    namespace = FieldProperty(schemas.ISimpleCloudWatchAlarm["namespace"])
    period = FieldProperty(schemas.ISimpleCloudWatchAlarm["period"])
    evaluation_periods = FieldProperty(schemas.ISimpleCloudWatchAlarm["evaluation_periods"])
    threshold = FieldProperty(schemas.ISimpleCloudWatchAlarm["threshold"])
    comparison_operator = FieldProperty(schemas.ISimpleCloudWatchAlarm["comparison_operator"])
    statistic = FieldProperty(schemas.ISimpleCloudWatchAlarm["statistic"])
    dimensions = FieldProperty(schemas.ISimpleCloudWatchAlarm["dimensions"])

    def __init__(self, __parent__):
        self.__parent__ = __parent__
        self.dimensions = []


@implementer(schemas.ICloudWatchAlarm)
class CloudWatchAlarm(Alarm):
    "CloudWatch Alarm"
    type = "Alarm"
    comparison_operator = FieldProperty(schemas.ICloudWatchAlarm["comparison_operator"])
    dimensions = FieldProperty(schemas.ICloudWatchAlarm["dimensions"])
    enable_ok_actions = FieldProperty(schemas.ICloudWatchAlarm["enable_ok_actions"])
    enable_insufficient_data_actions = FieldProperty(schemas.ICloudWatchAlarm["enable_insufficient_data_actions"])
    evaluate_low_sample_count_percentile = FieldProperty(schemas.ICloudWatchAlarm["evaluate_low_sample_count_percentile"])
    evaluation_periods = FieldProperty(schemas.ICloudWatchAlarm["evaluation_periods"])
    extended_statistic = FieldProperty(schemas.ICloudWatchAlarm["extended_statistic"])
    namespace = FieldProperty(schemas.ICloudWatchAlarm["namespace"])
    metric_name = FieldProperty(schemas.ICloudWatchAlarm["metric_name"])
    period = FieldProperty(schemas.ICloudWatchAlarm["period"])
    threshold = FieldProperty(schemas.ICloudWatchAlarm["threshold"])
    treat_missing_data = FieldProperty(schemas.ICloudWatchAlarm["treat_missing_data"])
    statistic = FieldProperty(schemas.ICloudWatchAlarm["statistic"])

    troposphere_props = troposphere.cloudwatch.Alarm.props
    cfn_mapping = {
        # 'AlarmName': computed by CloudFormation service so you can specify updates
        # 'AlarmDescription': computed in template for the SNS Topic ARNs
        # 'Dimensions': computed in template,
        # 'AlarmActions': computed in template,
        # 'OKActions': computed in template,
        # 'InsufficientDataActions': copmuted in template,
        'ActionsEnabled': 'actions_enabled',
        'ComparisonOperator': 'comparison_operator',
        'EvaluateLowSampleCountPercentile': 'evaluate_low_sample_count_percentile',
        'EvaluationPeriods': 'evaluation_periods',
        'ExtendedStatistic': 'extended_statistic',
        'MetricName': 'metric_name',
        # 'Namespace': computed in template
        'Period': 'period',
        'Statistic': 'statistic',
        'Threshold': 'threshold',
        'TreatMissingData': 'treat_missing_data',
        # 'Unit': (basestring, False),
        # 'DatapointsToAlarm': (positive_integer, False),
        #  'Metrics': ([MetricDataQuery], False),
    }

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self._extra_alarm_description = {}

    def threshold_human(self):
        "Human readable threshold"
        comparison = vocabulary.cloudwatch_comparison_operators[self.comparison_operator]
        if self.period < 60:
            period_human = '{} seconds'.format(int(self.period))
        elif self.period < 120:
            period_human = '{} minute'.format(int(self.period / 60))
        elif self.period < 3600:
            period_human = '{} minutes'.format(int(self.period / 60))
        elif self.period < 7200:
            period_human = '{} hour'.format(int(self.period / 3600))
        else:
            period_human = '{} hours'.format(int(self.period / 3600))
        return '{} {} {} for {} datapoints within {}'.format(
            self.metric_name,
            comparison,
            self.threshold,
            self.evaluation_periods,
            period_human
        )

    def get_alarm_description(self, notification_cfn_refs):
        """Create an Alarm Description in JSON format with Paco Alarm information"""
        project = get_parent_by_interface(self, schemas.IProject)
        netenv = get_parent_by_interface(self, schemas.INetworkEnvironment)
        env = get_parent_by_interface(self, schemas.IEnvironment)
        envreg = get_parent_by_interface(self, schemas.IEnvironmentRegion)
        app = get_parent_by_interface(self, schemas.IApplication)
        group = get_parent_by_interface(self, schemas.IResourceGroup)
        resource = get_parent_by_interface(self, schemas.IResource)

        # SNS Topic ARNs are supplied Paramter Refs
        topic_arn_subs = []
        sub_dict = {}
        for action_ref in notification_cfn_refs:
            ref_id = action_ref.data['Ref']
            topic_arn_subs.append('${%s}' % ref_id)
            sub_dict[ref_id] = action_ref

        # Notification Config
        notification_config = self.get_notifications_config(match_with_alarm=True)
        notifications_dict = {}
        if notification_config != None:
            notification_ref = '.'.join(notification_config.paco_ref_parts.split('.')[4:])
            notifications_dict[notification_config.name] = {
                'groups': notification_config.groups,
                'ref': notification_ref
            }

        # Base alarm info - used for standalone alarms not part of an application
        description = {
            "ref": self.paco_ref_parts,
            "project_name": project.name,
            "project_title": project.title,
            "account_name": self.account_name,
            "alarm_name": self.name,
            "classification": self.classification,
            "severity": self.severity,
            # "notification_groups": self.notification_groups,
            "topic_arns": topic_arn_subs,
            "notifications": notifications_dict
        }

        if paco.models.registry.CW_ALARM_DESCRIPTION_HOOK != None:
            description = paco.models.registry.CW_ALARM_DESCRIPTION_HOOK(self, description)

        # conditional fields
        if self.description:
            description['description'] = self.description
        if self.runbook_url:
            description['runbook_url'] = self.runbook_url

        if app != None:
            # Service applications and apps not part of a NetEnv
            description["app_name"] = app.name
            description["app_title"] = app.title
        if group != None:
            # Application level Alarms do not have resource group and resource
            description["resource_group_name"] = group.name
            description["resource_group_title"] = group.title
            if schemas.ITargetGroup.providedBy(resource):
                target_groups = resource.__parent__
                loadbalancer = target_groups.__parent__

                resource_name = f'{loadbalancer.name}.{target_groups.name}.{resource.name}'
                resource_title = f'{loadbalancer.name}.{target_groups.title}.{resource.title}'
            else:
                resource_name = resource.name
                resource_title = resource.title
            description["resource_name"] = resource_name
            description["resource_title"] = resource_title

        if netenv != None:
            # NetEnv information
            description["netenv_name"] = netenv.name
            description["netenv_title"] = netenv.title
            description["env_name"] = env.name
            description["env_title"] = env.title
            description["envreg_name"] = envreg.name
            description["envreg_title"] = envreg.title

        # add any extended fields
        description = self.extend_description(description)

        # bake into JSON
        description_json = json.dumps(description)
        return troposphere.Sub(
            description_json,
            sub_dict
        )

    def get_notifications_config(self, match_with_alarm=False):
        node = self
        notifications_config = None
        if node.notifications != None and len(node.notifications.keys()) > 0:
            notifications_config = self.notifications
        else:
            while notifications_config == None and node.__parent__ != None and schemas.IApplication.providedBy(node) == False:
                if hasattr(node, 'monitoring') and hasattr(node.monitoring, 'notifications') and node.monitoring.notifications != None and len(node.monitoring.notifications.keys()) > 0:
                    notifications_config = node.monitoring.notifications
                else:
                    node = node.__parent__

        if notifications_config == None:
            if schemas.IApplication.providedBy(node) and hasattr(node, 'notifications') and len(node.notifications.keys()) > 0:
                notifications_config = node.notifications


        if match_with_alarm == True and notifications_config != None:
            for alarm_notification in notifications_config.values():
                notification_severity = None
                if alarm_notification.severity and len(alarm_notification.severity) > 0:
                    notification_severity = alarm_notification.severity
                notification_classification = None
                if alarm_notification.classification and len(alarm_notification.classification) > 0:
                    notification_classification = alarm_notification.classification

                # Only include the groups that match the alarm
                notification_match = False
                if notification_severity == None:
                    severity_match = "none"
                elif self.severity == notification_severity:
                    severity_match = "same"
                else:
                    severity_match = "different"

                if notification_classification == None:
                    classification_match = "none"
                elif self.classification == notification_classification:
                    classification_match = "same"
                else:
                    classification_match = "different"

                if severity_match == "none" and classification_match == "none":
                    notification_match = True
                elif severity_match == "same" and classification_match == "same":
                    notification_match = True
                elif classification_match == "same" and severity_match == "none":
                    notification_match = True
                elif classification_match == "none" and severity_match == "same":
                    notification_match = True

                if notification_match == True:
                    return alarm_notification
            return None

        return notifications_config

    def add_to_alarm_description(self, add_dict):
        "Adds additional fields to AlarmDescription"
        for key, value in add_dict.items():
            if key in self._extra_alarm_description:
                raise paco.models.exceptions.AlarmDescriptionExtensionConflict(
                   f"Another extension has already added the field name '{key}' to AlarmDescription."
                )
            self._extra_alarm_description[key] = value
        return

    def extend_description(self, description):
        "Extend a description dict with any extra fields"
        for key, value in self._extra_alarm_description.items():
            if key in description:
                raise paco.models.exceptions.AlarmDescriptionExtensionConflict(
                   f"Can not extend AlarmDescription with the field name '{key}' as it's a Paco AlarmDescription reserved name."
                )
            description[key] = value
        return description


@implementer(schemas.ICloudWatchLogAlarm)
class CloudWatchLogAlarm(CloudWatchAlarm):
    log_set_name = FieldProperty(schemas.ICloudWatchLogAlarm["log_set_name"])
    log_group_name = FieldProperty(schemas.ICloudWatchLogAlarm["log_group_name"])

@implementer(schemas.IMonitorable)
class Monitorable():
    monitoring = FieldProperty(schemas.IMonitorable["monitoring"])

@implementer(schemas.IMetric)
class Metric():
    name = FieldProperty(schemas.IMetric["name"])
    measurements = FieldProperty(schemas.IMetric["measurements"])
    collection_interval = FieldProperty(schemas.IMetric["collection_interval"])
    resources = FieldProperty(schemas.IMetric["resources"])
    drop_device = FieldProperty(schemas.IMetric["drop_device"])

    def __init__(self):
        self.resources = []

# AWS Provided Metrics
ec2core_builtin_metric = Metric()
ec2core_builtin_metric.name = 'ec2core_builtin_metric'
ec2core_builtin_metric.collection_interval = 300
ec2core_builtin_metric.measurements = [
    'CPUUtilization',
    'DiskReadBytes',
    'DiskReadOps',
    'DiskWriteBytes',
    'DiskWriteOps',
    'NetworkIn',
    'NetworkOut',
    'StatusCheckFailed',
    'StatusCheckFailed_Instance',
    'StatusCheckFailed_System'
]

asg_builtin_metrics = [
    'GroupMinSize',
    'GroupMaxSize',
    'GroupDesiredCapacity',
    'GroupInServiceInstances',
    'GroupPendingInstances',
    'GroupStandbyInstances',
    'GroupTerminatingInstances',
    'GroupTotalInstances'
]

@implementer(schemas.IMonitorConfig)
class MonitorConfig(Deployable, Named):
    collection_interval = FieldProperty(schemas.IMonitorConfig["collection_interval"])
    metrics = FieldProperty(schemas.IMonitorConfig["metrics"])
    asg_metrics = FieldProperty(schemas.IMonitorConfig["asg_metrics"])
    notifications = FieldProperty(schemas.IMonitorConfig["notifications"])

    def __init__(self, name, __parent__):
        super().__init__(name, __parent__)
        self.alarm_sets = AlarmSets('alarm_sets', self)
        self.health_checks = HealthChecks('health_checks', self)
        self.log_sets = CloudWatchLogSets('log_sets', self)
        self.notifications = AlarmNotifications('notifications', self)
        self.asg_metrics = asg_builtin_metrics
        self.metrics = []

@implementer(schemas.IDashboardVariables)
class DashboardVariables(Named, dict):
    pass

@implementer(schemas.ICloudWatchDashboard)
class CloudWatchDashboard(ApplicationResource):
    dashboard_file = FieldProperty(schemas.ICloudWatchDashboard["dashboard_file"])
    dashboard_name = FieldProperty(schemas.ICloudWatchDashboard["dashboard_name"])
    variables = FieldProperty(schemas.ICloudWatchDashboard["variables"])
