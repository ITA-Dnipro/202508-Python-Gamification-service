"""
Default ExpAction records to be created on application startup.
These represent common gamification actions across the platform.
"""

DEFAULT_EXP_ACTIONS = [
    {
        "name": "profile_complete",
        "exp_value": 50,
        "description": "Successfully register on MiniF platform",
        "role": None,
        "repeatable": False,
    },
    {
        "name": "startup_profile_complete",
        "exp_value": 50,
        "description": "Complete startup profile with all required fields",
        "role": "startup",
        "repeatable": False,
    },
    {
        "name": "investor_profile_complete",
        "exp_value": 50,
        "description": "Complete investor profile with all required fields",
        "role": "investor",
        "repeatable": False,
    },
    {
        "name": "first_project_created",
        "exp_value": 250,
        "description": "Create your first project",
        "role": "startup",
        "repeatable": False,
    },
    {
        "name": "project_created",
        "exp_value": 150,
        "description": "Create your new project",
        "role": "startup",
        "repeatable": True,
    },
    {
        "name": "first_comment_created",
        "exp_value": 25,
        "description": "Add your first comment to a project",
        "role": None,
        "repeatable": False,
    },
    {
        "name": "comment_created",
        "exp_value": 5,
        "description": "Add a comment to a project",
        "role": None,
        "repeatable": True,
    },
    {
        "name": "investment_made",
        "exp_value": 250,
        "description": "Make an investment in a project",
        "role": "investor",
        "repeatable": True,
    },
    {
        "name": "investment_got",
        "exp_value": 150,
        "description": "Get an investment from an investor in a project",
        "role": "startup",
        "repeatable": True,
    },
    {
        "name": "investment_goal_met",
        "exp_value": 500,
        "description": "Meet the investment goal for your project",
        "role": "startup",
        "repeatable": True,
    },
    {
        "name": "daily_login",
        "exp_value": 10,
        "description": "Log in to the platform (once per day)",
        "role": None,
        "repeatable": True,
    },
    {
        "name": "received_like",
        "exp_value": 2,
        "description": "Receive a like on your project",
        "role": "startup",
        "repeatable": True,
    },
]
