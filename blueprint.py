# Register this blueprint by adding the following line of code
# to your entry point file.
# app.register_functions(blueprint)
#
# Please refer to https://aka.ms/azure-functions-python-blueprints
import logging
import azure.functions as func

blueprint = func.Blueprint()


@blueprint.event_grid_trigger(arg_name="azeventgrid")
def EventGridTriggerV3(azeventgrid: func.EventGridEvent):
    logging.info('Python EventGrid trigger processed an event')
