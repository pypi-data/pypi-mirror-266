# MaiTai Python SDK Guide

Welcome to the MaiTai Python SDK guide. This document will help you get started with integrating the MaiTai SDK into your application for evaluating AI outputs. Follow the steps below to install, configure, and use the SDK effectively.

## Installation

To install the MaiTai SDK, run the following command in your terminal:

```bash
pip install maitai-sdk-python
```

## Configuration

Before you can start evaluating AI outputs, you need to initialize the SDK with your `application_id` and `api_key`. These credentials are essential for authenticating your requests to the MaiTai service.

1. Obtain your `application_id` and `api_key` from the MaiTai platform.
2. Initialize the SDK in your application as shown below:

```python
import maitai

maitai.initialize('your_api_key_here', app_id)
```

## Updating Application Context

Application context is information that's pertinent to the overall application and changes infrequently. To update or append to the application context, use the `update_application_context` or `append_application_context` methods of the `Evaluator` class, respectively. Here's how:

### Updating Application Context

```python
import maitai

# The context you want to update
context = {
    'restaurant_name': 'Bob\'s Burgers',
    'menu': ['burger', 'fries', 'soda']
}

# Update the application context
maitai.Evaluator.update_application_context(context)
```

### Appending to Application Context

```python
import maitai

# The context you want to append
context_to_append = {
    'hours': ['Sunday: 10:00 AM - 22:00 PM', 'Monday: 10:00 AM - 22:00 PM', 'Tuesday: 10:00 AM - 22:00 PM', 'Wednesday: 10:00 AM - 22:00 PM', 'Thursday: 10:00 AM - 22:00 PM', 'Friday: 10:00 AM - 22:00 PM', 'Saturday: 10:00 AM - 22:00 PM']
}

# Append to the application context
maitai.Evaluator.append_application_context(context_to_append)
```

## Updating Session Context

Before evaluating AI output, you may need to update the session context with relevant information. This context helps in tailoring the evaluation process. Follow these steps to update the session context:

1. Ensure your `application_id` and `api_key` are set as described in the Configuration section.
2. Use the `update_session_context` method of the `Evaluator` class, providing a `session_id` and a context dictionary. The `session_id` is an identifier of your choosing, and the context is a dictionary of key-value pairs, where the key describes the context piece passed as the value.

Here's an example of how to update the session context:

```python
import maitai

# Your session ID and the context you want to update
session_id = 'your_session_id_here'
context = {
    'customer_name': 'John Doe',
    'conversation': 'AI: Hi. How can I help you today?\nCX: I would like to place an order for a burger.\nAI: I can help you with that. What type of burger would you like?\nCX: I would like a medium burger with cheese.'
}

# Update the session context
maitai.Evaluator.update_session_context(session_id, context)
```

### Appending to Session Context

To append to an existing session context, use the `append_session_context` method of the `Evaluator` class. This method allows you to add new key-value pairs to the existing context or override the values of existing keys. Here's how you can append to the session context:

```python
import maitai

# Your session ID and the context you want to append
session_id = 'your_session_id_here'
context_to_append = {
    'cart': [{'item': 'burger', 'quantity': 1}, {'item': 'fries', 'quantity': 1}, {'item': 'soda', 'quantity': 1}]  # This will override if 'cart' already exists
}

# Append to the session context
maitai.Evaluator.append_session_context(session_id, context_to_append)
```

## Evaluating AI Output

To evaluate AI output, you'll need to use the `Evaluator` class provided by the SDK. When evaluating content, you must provide a `session_id`, a `reference_id`, and the content itself. The `reference_id` is a unique identifier created by you, used to tie the evaluation request back to an item in your system. Here's an example:

```python
import maitai

# Your session ID, reference ID, and the content you want to evaluate
session_id = 'your_session_id_here'
reference_id = 'your_reference_id_here'  # Unique identifier for tying back to your system
content = 'AI: Sure thing. Is there anything else I can get you today?'

# Evaluate the content
maitai.Evaluator.evaluate(session_id, reference_id, content)
```

This will send the evaluation request to the MaiTai service asynchronously. Ensure that your `application_id` and `api_key` are correctly set as shown in the Configuration section above.

## Conclusion

You're now ready to start using the MaiTai Python SDK to evaluate AI outputs in your application. Remember to follow best practices for managing your `api_key` and `application_id` securely within your application. If you encounter any issues or have further questions, refer to the [MaiTai Documentation](https://docs.maitai.ai) or reach out to the support team.
