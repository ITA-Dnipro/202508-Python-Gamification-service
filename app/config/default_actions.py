"""
Default ExpAction records to be created on application startup.
These represent common gamification actions across the platform.
"""
EXP_SMALL = 5
EXP_MEDIUM = 50
EXP_BIG = 150
EXP_LARGE = 250
EXP_HUGE = 500

DEFAULT_EXP_ACTIONS = [
    {
        "name": "profile_complete",
        "exp_value": EXP_MEDIUM,
        "description": "Successfully register on MiniF platform",
        "role": None,
        "repeatable": False,
    },
    {
        "name": "startup_profile_complete",
        "exp_value": EXP_MEDIUM,
        "description": "Complete startup profile with all required fields",
        "role": "startup",
        "repeatable": False,
    },
    {
        "name": "investor_profile_complete",
        "exp_value": EXP_MEDIUM,
        "description": "Complete investor profile with all required fields",
        "role": "investor",
        "repeatable": False,
    },
    {
        "name": "first_project_created",
        "exp_value": EXP_LARGE,
        "description": "Create your first project",
        "role": "startup",
        "repeatable": False,
    },
    {
        "name": "project_created",
        "exp_value": EXP_BIG,
        "description": "Create your new project",
        "role": "startup",
        "repeatable": True,
    },
    {
        "name": "first_comment_created",
        "exp_value": EXP_MEDIUM,
        "description": "Add your first comment to a project",
        "role": None,
        "repeatable": False,
    },
    {
        "name": "comment_created",
        "exp_value": EXP_SMALL,
        "description": "Add a comment to a project",
        "role": None,
        "repeatable": True,
    },
    {
        "name": "investment_made",
        "exp_value": EXP_LARGE,
        "description": "Make an investment in a project",
        "role": "investor",
        "repeatable": True,
    },
    {
        "name": "investment_got",
        "exp_value": EXP_BIG,
        "description": "Get an investment from an investor in a project",
        "role": "startup",
        "repeatable": True,
    },
    {
        "name": "investment_goal_met",
        "exp_value": EXP_HUGE,
        "description": "Meet the investment goal for your project",
        "role": "startup",
        "repeatable": True,
    },
    {
        "name": "daily_login",
        "exp_value": EXP_SMALL,
        "description": "Log in to the platform (once per day)",
        "role": None,
        "repeatable": True,
    },
    {
        "name": "received_like",
        "exp_value": EXP_SMALL,
        "description": "Receive a like on your project",
        "role": "startup",
        "repeatable": True,
    },
]
