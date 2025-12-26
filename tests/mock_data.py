"""Mock data for testing"""
from datetime import datetime, timedelta


def generate_mock_messages(count: int = 20, chat_id: int = -1001234567890):
    """
    Generate mock message data for testing
    
    Args:
        count: Number of messages to generate
        chat_id: Chat ID (negative for groups)
    
    Returns:
        List of mock message dictionaries
    """
    users = [
        {'id': 123456, 'username': 'alice', 'first_name': 'Alice'},
        {'id': 234567, 'username': 'bob', 'first_name': 'Bob'},
        {'id': 345678, 'username': 'charlie', 'first_name': 'Charlie'},
        {'id': 456789, 'username': 'diana', 'first_name': 'Diana'}
    ]
    
    conversations = [
        "Hey everyone! What do you think about the new feature?",
        "I think it's great! Really improves the workflow.",
        "Agreed! Though I noticed a small bug in the UI.",
        "Can you describe the bug? I'll look into it.",
        "Sure, when you click the submit button twice quickly, it duplicates the entry.",
        "Ah, classic race condition. I'll add a debounce.",
        "Thanks! Also, the performance seems better now.",
        "Yeah, we optimized the database queries last week.",
        "Nice work team! When is the next release scheduled?",
        "Planning for next Friday. We should run tests by Wednesday.",
        "I can help with testing. What areas need coverage?",
        "Mainly the payment flow and user authentication.",
        "Got it. I'll start on Monday.",
        "Perfect. Let me know if you need any test data.",
        "Will do! By the way, did anyone see the analytics dashboard?",
        "Yes! The new charts are much more readable.",
        "Glad you like them. We used D3.js for the visualizations.",
        "Makes sense. They're very smooth.",
        "Should we add export functionality too?",
        "Good idea! CSV and PDF exports would be useful."
    ]
    
    mock_messages = []
    base_time = datetime.now() - timedelta(hours=2)
    
    for i in range(min(count, len(conversations))):
        user = users[i % len(users)]
        mock_messages.append({
            'chat_id': chat_id,
            'message_id': 1000 + i,
            'user_id': user['id'],
            'username': user['username'],
            'text': conversations[i],
            'timestamp': base_time + timedelta(minutes=i * 5),
            'is_system_message': False,
            'has_photo': False,
            'has_video': False,
            'has_document': False,
            'caption': None
        })
    
    return mock_messages


def generate_mock_media_messages():
    """Generate mock messages with media attachments"""
    return [
        {
            'chat_id': -1001234567890,
            'message_id': 2001,
            'user_id': 123456,
            'username': 'alice',
            'text': '',
            'timestamp': datetime.now(),
            'has_photo': True,
            'caption': 'Check out this screenshot of the bug'
        },
        {
            'chat_id': -1001234567890,
            'message_id': 2002,
            'user_id': 234567,
            'username': 'bob',
            'text': '',
            'timestamp': datetime.now(),
            'has_video': True,
            'caption': 'Demo video of the new feature'
        },
        {
            'chat_id': -1001234567890,
            'message_id': 2003,
            'user_id': 345678,
            'username': 'charlie',
            'text': '',
            'timestamp': datetime.now(),
            'has_document': True,
            'caption': None
        }
    ]


def generate_mock_system_messages():
    """Generate mock system messages"""
    return [
        {
            'chat_id': -1001234567890,
            'message_id': 3001,
            'user_id': None,
            'username': 'System',
            'text': 'Alice joined the group',
            'timestamp': datetime.now(),
            'is_system_message': True
        },
        {
            'chat_id': -1001234567890,
            'message_id': 3002,
            'user_id': None,
            'username': 'System',
            'text': 'Bob left the group',
            'timestamp': datetime.now(),
            'is_system_message': True
        }
    ]


# Professional conversation for testing different summary styles
PROFESSIONAL_CONVERSATION = [
    "alice: Good morning team. Let's discuss Q4 objectives.",
    "bob: We need to focus on customer retention metrics.",
    "charlie: Agreed. I've prepared a detailed analysis.",
    "diana: The data shows a 15% improvement in satisfaction scores.",
    "alice: Excellent. What are the key drivers?",
    "bob: Faster response times and proactive support.",
    "charlie: We should implement automated follow-ups.",
    "diana: I can create a workflow for that by next week."
]

# Casual conversation
CASUAL_CONVERSATION = [
    "alice: omg did you see the game last night?? 🏀",
    "bob: yessss! that last shot was insane!",
    "charlie: i missed it 😭 anyone got a link?",
    "diana: ill send you the highlights",
    "alice: also who wants to grab lunch later?",
    "bob: im in! that new pizza place?",
    "charlie: sounds good to me 🍕",
    "diana: count me in too!"
]

# Technical conversation
TECHNICAL_CONVERSATION = [
    "alice: The API is returning 500 errors on POST /users",
    "bob: Checking the logs... looks like a database connection timeout",
    "charlie: We might need to increase the pool size",
    "diana: Or add connection retry logic with exponential backoff",
    "alice: Good idea. Current timeout is 5s, probably too low",
    "bob: I'll update it to 30s and add retries",
    "charlie: Also seeing high CPU usage around that time",
    "diana: Could be related. Let's add some profiling."
]
