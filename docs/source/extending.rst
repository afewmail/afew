Extending afew
==============

You can put python files in `~/.config/afew/` and they will be imported by
afew.  If you use that python file to define a `Filter` class and use the
`register_filter` decorator then you can refer to it in your filter
configuration.

So an example small filter you could add might be:

.. code-block:: python

    from afew.Filter import Filter, register_filter

    PROJECT_MAPPING = {
        'fabric': 'deployment',
        'oldname': 'new-name',
    }

    @register_filter
    class RedmineFilter(Filter):
        message = 'Create tag based on redmine project'
        query = 'NOT tag:redmine'

        def handle_message(self, message):
            project = message.get_header('X-Redmine-Project')
            if project in PROJECT_MAPPING:
                project = PROJECT_MAPPING[project]
            self.add_tags(message, 'redmine', project)

We have defined the `message` and `query` class variables that are used
by the parent class `Filter`.  The `message` is printed when running with
verbose flags.  The `query` is used to select messages to run against - here
we ensure we don't bother looking at messages we've already looked at.

The `handle_message()` method is the key one to implement.  This will be called
for each message that matches the query.  The argument is a `notmuch message object`_
and the key methods used by the afew filters are `get_header()`, `get_filename()`
and `get_thread()`.

.. _notmuch message object: http://pythonhosted.org/notmuch/#message-a-single-message

Of the methods inherited from the `Filter` class the key ones are `add_tags()` and
`remove_tags()`, but read about the :doc:`implementation` or just read the source
code to get your own ideas.

Once you've defined your filter, you can add it to your config like any other filter:

.. code-block:: ini

    [RedmineFilter]
