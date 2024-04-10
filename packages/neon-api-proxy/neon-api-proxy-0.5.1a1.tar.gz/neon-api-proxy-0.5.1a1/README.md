# NeonAI API Proxy
Proxies API calls to consolidate usage to a single point and allow for caching of API data.

## Request Format
API requests should be in the form of a dictionary. The service requested should be specified as `service` and the 
remaining data will be passed to the `handle_query` method of the requested service as kwargs.

>Example Wolfram|Alpha Request:
>```json
>{
>  "service": "wolfram_alpha",
>  "query": "how far away is Rome?",
>  "api": "simple",
>  "units": "metric",
>  "ip": "64.34.186.120"
>}
>```

## Response Format
Responses will be returned as dictionaries. Responses should contain the following:
- `status_code` - Usually contains the HTTP status code from the requested API, `-1` should be used to specify any other errors
- `content` - Usually contains the HTTP content (bytes) from the requested API, but may include a string message for errors.
- `encoding` = Usually contains the HTTP content encoding if content is the byte representation of a string, may be `None`

## Docker Configuration
When running this as a docker container, the `XDG_CONFIG_HOME` envvar is set to `/config`.
A configuration file at `/config/neon/diana.yaml` is required and should look like:
```yaml
MQ:
  port: <MQ Port>
  server: <MQ Hostname or IP>
  users:
    neon_api_connector:
      password: <neon_api user's password>
      user: neon_api
keys:
  api_services:
    alpha_vantage:
      api_key: <Alpha Vantage Key>
    open_weather_map:
      api_key: <OWM Key>
    wolfram_alpha:
      api_key: <Wolfram|Alpha Key>
```

For example, if your configuration resides in `~/.config`:
```shell
export CONFIG_PATH="/home/${USER}/.config"
docker run -v ${CONFIG_PATH}:/config neon_api_proxy
```
> Note: If connecting to a local MQ server, you may need to specify `--network host`