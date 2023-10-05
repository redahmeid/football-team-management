import serverless_sdk
sdk = serverless_sdk.SDK(
    org_id='redahmeid',
    application_name='football-team-management',
    app_uid='X8h4p21tflJw7f5ZKb',
    org_uid='d89014f8-1e4c-4c62-bdda-3282d3b63863',
    deployment_uid='89f29e8d-4b6c-41ed-875b-6626b3fe1844',
    service_name='football-team-management',
    should_log_meta=True,
    should_compress_logs=True,
    disable_aws_spans=False,
    disable_http_spans=False,
    stage_name='dev',
    plugin_version='7.0.5',
    disable_frameworks_instrumentation=False,
    serverless_platform_stage='prod'
)
handler_wrapper_kwargs = {'function_name': 'football-team-management-dev-create_club', 'timeout': 6}
try:
    user_handler = serverless_sdk.get_user_handler('handler.create_club')
    handler = sdk.handler(user_handler, **handler_wrapper_kwargs)
except Exception as error:
    e = error
    def error_handler(event, context):
        raise e
    handler = sdk.handler(error_handler, **handler_wrapper_kwargs)
