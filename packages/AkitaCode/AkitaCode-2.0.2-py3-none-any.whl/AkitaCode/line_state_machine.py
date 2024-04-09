from .keys import State


def create_line_state_machine():
    """
    Crea la màquina d'estats del parsejador de línia.

    :return: L'estat origen de la màquina d'estats.
    :rtype: State
    """
    # Creació de l'origen de la màquina d'estats.
    root = State(0,error_msg="Unexpected keyword ''{}'' at first word of line.")
    
    # Creació dels Estats de la comanda import.
    import_instance = State(
        id=1000,
        command="import",
        strict=True,
        error_msg="Unexpected keyword ''{}'' after ''import'' statement.")
    
    import_protocol = State(
        id=1001,
        command="protocol",
        error_msg="Requiered protocol name after ''protocol'' statement.")
    
    import_name_protocol = State(
        id=1002,
        command="<name>", 
        strict=False,
        error_msg="More than expected statements. ''{}'' not expected.")
    
    # Creació dels Estats de la comanda //.
    comment = State(999990, required=False, command="//",allow_reserved_words=True)
    comment_msg = State(999991, required=False, strict=False, command="<msg>",allow_reserved_words=True)
    comment_msg2 = State(999992, required=False, strict=False, command="<msg>",allow_reserved_words=True)

    # Creació dels Estats de la comanda create.
    create_instance = State(
        id=2000,
        command="create",
        error_msg="Unexpected keyword ''{}'' after ''create'' instance."
    )

    # ### SITUATION ###
    
    situation_statement = State(
        id=2100,
        command="situation",
        error_msg="Requiered situation name after ''situation'' statement. Use ''_'' to generate automatically an alias."
    )

    situation_name = State(
        id=2101,
        command="<name>",
        strict=False,
        error_msg="Expected keyword ''with'' after name situation statement."
    )

    with_under_situation = State(
        id=2102,
        command="with",
        error_msg="Unexpected keyword ''{}'' after ''with'' keyword."
    )
    
    time_under_situation = State(
        id=2103,
        command="time",
        error_msg="Invalid time expression ''{}'' in miliseconds. Float time not be allowed."
    )

    set_time_under_situation = State(
        id=2104,
        command="<time>",
        error_msg="No required more arguments after time situation value. ''{}'' not expected.",
        required=True,
        strict=False,
    )

    # ### ENVIROMENT ###

    enviroment_instance = State(
        id=2200,
        command="enviroment",
        error_msg="Requiered enviroment name after ''enviroment'' statement. Use ''_'' to generate automatically an alias."
    )

    enviroment_name = State(
        id=2201,
        command="<name>",
        error_msg="No required more arguments after time situation value. ''{}'' not expected.",
        strict=False,
        required=True
    )

    # Creació dels Estats de la comanda var.

    variable_instance = State(
        id=3000,
        command="var",
        error_msg="Expected variable name after variable instance."
    )

    variable_name = State(
        id=3001,
        command="<name>",
        error_msg="Invalid assignment after variable name. To assign value to variable use: ''='' after variable name.",
        strict=False,
        required=True
    )

    variable_assignament = State(
        id=3002,
        command="=",
        error_msg="Expected value after assignment expression."
    )

    variable_value = State(
        id=3003,
        command="<value>",
        error_msg="No required more arguments after variable value. ''{}'' not expected.",
        required=True,
        strict=False
    )

    # Creació dels Estats de la comanda fn.

    function_instance = State(
        id=4000,
        command="fn",
        error_msg="Expected function name after ''fn'' statement."
    )

    function_name = State(
        id=4001,
        command="<name>",
        error_msg="Open query ''('' is required after function name. ''{}'' not expected.",
        strict=False
    )

    function_open_query = State(
        id=4002,
        command="(",
        error_msg="Expected an attribute of function after open query directive."
    )

    atribute1_name = State(
        id=4003,
        command="<attribute>",
        error_msg="Expected value for function attribute.",
        required=True,
        strict=False
    )

    atribute1_value = State(
        id=4004,
        command="<value>",
        error_msg="Expected pipe ''|'' or close query directive '')''.",
        required=True,
        strict=False
    )

    pipe_argument = State(
        id=4005,
        command="|",
        error_msg="Expected an attribute of function after pipe directive.",
        strict=True,
        required=False
    )

    atribute2_name = State(
        id=4006,
        command="<attribute>",
        error_msg="Expected value for function attribute.",
        strict=False,
        required=True
    )

    atribute2_value = State(
        id=4007,
        command="<value>",
        error_msg="Expected pipe ''|'' or close query directive '')''.",
        strict=False
    )

    function_close_query = State(
        id=4008,
        command=")",
        error_msg="No required more arguments after close query. ''{}'' not expected."
    )


    # Creació dels Estats de la comanda end.

    end_statement = State(
        id=10001,
        command="end",
        error_msg="Unexpected argument {} after end statement."
    )



    # Creació dels Estats de la comanda for.

    for_instance = State(
        id=5000,
        command="for",
        error_msg="Expected condition after ''for'' statement."
    )

    for_each = State(
        id=5001,
        command="each",
        error_msg="Expected ''case'' keyword after conditions."
    )

    for_case = State(
        id=5002,
        command="case",
        error_msg="Expected ''of'' keyword after all cases declaration."
    )

    for_of = State(
        id=5003,
        command="of",
        error_msg="Expected open query ''('' statment after ''of''."
    )

    for_openquery = State(
        id=5004,
        command="(",
        error_msg="Expected output variable after open query statement."
    )

    for_variable1 = State(
        id=5005,
        command="<variable>",
        error_msg="A comma or close query statement is expected.",
        strict=False
    )

    for_next_variable = State(
        id=5006,
        command=",",
        error_msg="Expected another output variable.",
        required=False
    )

    for_variable2 = State(
        id=5007,
        command="<variable>",
        error_msg="A comma or close query statement is expected.",
        strict=False,
        required=False
    )

    for_closequery = State(
        id=5008,
        command=")",
        error_msg="Expected ''do'' statement after close query."
    )

    for_do = State(
        id=5009,
        command="do",
        error_msg="No required more arguments after ''do'' statement. ''{}'' not expected."
    )



    # Creació dels Estats de la comanda time.

    time_instance = State(
        id=6000,
        command="time",
        error_msg="Expected time value after time statement."
    )

    time_value = State(
        id=6001,
        command="<time>",
        error_msg="No required more arguments after set time. ''{}'' not expected.",
        strict=False
    )


    # Insereix a la màquina d'estats les dependències de la comanda import.
    root.set_next(import_instance)
    root.set_next(comment)
    import_instance.set_next(import_protocol)
    import_protocol.set_next(import_name_protocol)
    import_name_protocol.set_next(root)


    # Insereix a la màquina d'estats les dependències de la comanda //.

    comment_msg.set_next(root)
    comment_msg2.set_next(root)
    comment_msg.set_next(comment_msg2)
    comment_msg2.set_next(comment_msg)
    comment.set_next(comment_msg)
    comment.set_next(root)

    # Insereix a la màquina d'estats les dependències de la comanda situation.
    
    root.set_next(create_instance)
    create_instance.set_next(situation_statement)
    situation_statement.set_next(situation_name)
    situation_name.set_next(with_under_situation)
    with_under_situation.set_next(time_under_situation)
    time_under_situation.set_next(set_time_under_situation)
    set_time_under_situation.set_next(root)

    # Insereix a la màquina d'estats les dependències de la comanda enviroment.

    create_instance.set_next(enviroment_instance)
    enviroment_instance.set_next(enviroment_name)
    enviroment_name.set_next(root)

    # Insereix a la màquina d'estats les dependències de la comanda var.

    root.set_next(variable_instance)
    variable_instance.set_next(variable_name)
    variable_name.set_next(root)
    variable_name.set_next(variable_assignament)
    variable_assignament.set_next(variable_value)
    variable_value.set_next(root)

    
    # Insereix a la màquina d'estats les dependències de la comanda fn.
    root.set_next(function_instance)
    function_instance.set_next(function_name)
    function_name.set_next(function_open_query)
    function_open_query.set_next(atribute1_name)
    atribute1_name.set_next(atribute1_value)
    atribute1_value.set_next(pipe_argument)
    atribute1_value.set_next(function_close_query)
    pipe_argument.set_next(atribute2_name)
    atribute2_name.set_next(atribute2_value)
    atribute2_value.set_next(pipe_argument)
    atribute2_value.set_next(function_close_query)
    function_close_query.set_next(root)


    # Insereix a la màquina d'estats les dependències de la comanda end.
    root.set_next(end_statement)
    end_statement.set_next(root)



    # Insereix a la màquina d'estats les dependències de la comanda for.

    root.set_next(for_instance)
    for_instance.set_next(for_each)
    for_each.set_next(for_case)
    for_case.set_next(for_of)
    for_of.set_next(for_openquery)
    for_openquery.set_next(for_variable1)
    for_variable1.set_next(for_next_variable)
    for_variable1.set_next(for_closequery)
    for_next_variable.set_next(for_variable2)
    for_variable2.set_next(for_next_variable)
    for_variable2.set_next(for_closequery)
    for_closequery.set_next(for_do)
    for_do.set_next(root)


    # Insereix a la màquina d'estats les dependències de la comanda for.
    root.set_next(time_instance)
    time_instance.set_next(time_value)
    time_value.set_next(root)

    # ############################# #
    return root