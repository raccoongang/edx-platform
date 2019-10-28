def plugin_settings(settings):
    # Queue to use for updating persistent grades
    settings.RECALCULATE_GRADES_ROUTING_KEY = settings.LOW_PRIORITY_QUEUE

    # Queue to use for updating grades due to grading policy change
    settings.POLICY_CHANGE_GRADES_ROUTING_KEY = settings.LOW_PRIORITY_QUEUE

    # Queue to send notification to user if he has reached the minimal grading score
    settings.MINIMAL_GRADING_REACHED_NOTIFICATION_ROUTING_KEY = settings.LOW_PRIORITY_QUEUE
