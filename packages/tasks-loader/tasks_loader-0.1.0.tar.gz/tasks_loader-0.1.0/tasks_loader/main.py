import csv, re

class Task:
    """
    Represents a single task, dynamically creating attributes based on input keyword arguments.
    
    Attributes:
        id (str): A unique identifier for the task, formatted as a zero-padded string.
    
    Parameters:
        **kwargs: Arbitrary keyword arguments representing task attributes and their values.
    """
    _id_counter = 1  # Class variable to keep track of the next id

    def __init__(self, **kwargs):
        self.id = str(Task._id_counter).zfill(3)  # Format the id as '001', '002',...
        Task._id_counter += 1  # Increment for the next task
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        """Return the task id as a string representation of the Task object."""
        return self.id

    def to_dict(self):
        """
        Convert the Task instance into a dictionary.
        
        Returns:
            dict: A dictionary representation of the Task instance, including its id and all dynamically added attributes.
        """
        return {**self.__dict__}

class Tasks:
    """
    Manages a collection of Task objects created from a CSV file based on a specified task format.
    
    Attributes:
        input_file (str): Path to the input CSV file containing task data.
        task_format (dict): A dictionary specifying the format and validation rules for task attributes.
        global_default (any): A global default value to be used for any attribute not explicitly set or invalid.
        tasks (list): A list of Task instances created from the input CSV file.
    """
    def __init__(self, input_file='tasks.csv', task_format=None, global_default=None):
        self.input_file = input_file
        self.task_format = task_format or {}
        self.tasks = []
        self.global_default = global_default
        self.load_tasks()

    @property
    def is_valid(self):
        """
        Check if there are any valid tasks loaded.
        
        Returns:
            bool: True if at least one task has been successfully loaded, False otherwise.
        """
        return bool(self.tasks)

    def __len__(self):
        """
        Get the number of tasks loaded.
        
        Returns:
            int: The number of tasks.
        """
        return len(self.tasks)

    def __iter__(self):
        """
        Allow iteration over the collection of tasks, yielding each task as a dictionary.
        
        Yields:
            dict: The dictionary representation of each task.
        """
        for task in self.tasks:
            yield task.to_dict() 

    def __str__(self):
        """
        Provide a string representation indicating the number of valid tasks loaded.
        
        Returns:
            str: A message stating the number of loaded tasks.
        """
        return f"Loaded {len(self.tasks)} valid tasks."

    def to_dict(self):
        """
        Convert all loaded tasks into a list of dictionaries.
        
        Returns:
            list: A list of dictionaries, each representing a Task instance.
        """
        return [task.to_dict() for task in self.tasks]

    def load_tasks(self):
        """
        Load tasks from the specified CSV file, validate them according to the task format, and create Task objects.
        """
        with open(self.input_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:

                # Convert empty strings to None or global default where appropriate
                processed_row = {key.lower().replace(" ", "_"): (self.global_default if value == '' else value) for key, value in row.items()}
                
                if self.is_valid_task(processed_row):
                    valid_data = {key.replace(" ", "_").lower(): self.cast_value(key, processed_row[key], self.task_format[key]['type']) 
                                for key in processed_row if key in self.task_format}
                    self.tasks.append(Task(**valid_data))

    def is_valid_task(self, task_data):
        """
        Validate a task based on the task format specifications.
        
        Parameters:
            task_data (dict): The task data to validate.
            
        Returns:
            bool: True if the task is valid, False otherwise.
        """
        for key, specs in self.task_format.items():
            if specs.get('required', False) and (key not in task_data or not self.is_valid_field(key, task_data[key])):
                return False
        return True

    def is_valid_field(self, key, value):
        """
        Validate an individual field based on its specifications in the task format.
        
        Parameters:
            key (str): The attribute name.
            value (any): The value of the attribute to validate.
            
        Returns:
            any: The validated and possibly transformed value, or the default value if validation fails.
        """
        specs = self.task_format[key]
        expected_type = specs['type']
        validation = specs.get('validation', None)
        choices = specs.get('choices', None)
        default = specs.get('default', self.global_default)
        
        # Use default value if value is missing
        if not value:
            return default

        # If a regex validation is specified
        if isinstance(validation, str):
            if not re.match(validation, value):
                return default  # Doesn't match regex
        
        # If a lambda validation is specified
        elif callable(validation):
            if not validation(value):
                return default  # Fails lambda validation

        # Attempt to cast the value to the expected type
        try:
            value = expected_type(value)
        except (ValueError, TypeError):
            return default

        # If choices are specified, check if the value is one of the choices
        if choices and value not in choices:
            return default

        return value

    def cast_value(self, key, value, expected_type):
        """
        Cast a value to the specified type and apply any post-formatting defined in the task format.
        
        Parameters:
            key (str): The attribute name.
            value (any): The value to cast and possibly transform.
            expected_type (type): The expected Python type for the value.
            
        Returns:
            any: The casted and possibly post-formatted value, or a default value if casting fails.
        """
        specs = self.task_format[key]
        post_format = specs.get('post_format', None)

        validated_value = self.is_valid_field(key, value)
        if validated_value is not False:
            if post_format:
                try:
                    # Apply post-formatting function
                    return post_format(validated_value)
                except Exception:
                    pass
            return validated_value
        
        return specs.get('default', self.global_default)