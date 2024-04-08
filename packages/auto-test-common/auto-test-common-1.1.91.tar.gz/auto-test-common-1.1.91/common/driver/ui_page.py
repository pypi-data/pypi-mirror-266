from playwright.sync_api import Page

class UIPage(Page):

    def UiGet(self,url: str, *,
        params: typing.Optional[
            typing.Dict[str, typing.Union[str, float, bool]]
        ] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        data: typing.Optional[typing.Union[typing.Any, bytes, str]] = None,
        form: typing.Optional[typing.Dict[str, typing.Union[str, float, bool]]] = None,
        multipart: typing.Optional[
            typing.Dict[str, typing.Union[bytes, bool, float, str, FilePayload]]
        ] = None,
        timeout: typing.Optional[float] = None,
        fail_on_status_code: typing.Optional[bool] = None,
        ignore_https_errors: typing.Optional[bool] = None,
        max_redirects: typing.Optional[int] = None):

        self.request.get((
        url,
        params,
        headers,
        data,
        form,
        multipart,
        timeout,
        fail_on_status_code,
        ignore_https_errors,
        max_redirects
    ))

    def UiDel(self,url: str, *,
        params: typing.Optional[typing.Dict[str, typing.Union[str, float, bool]]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        data: typing.Optional[typing.Union[typing.Any, bytes, str]] = None,
        form: typing.Optional[typing.Dict[str, typing.Union[str, float, bool]]] = None,
        multipart: typing.Optional[
            typing.Dict[str, typing.Union[bytes, bool, float, str, FilePayload]]
        ] = None,
        timeout: typing.Optional[float] = None,
        fail_on_status_code: typing.Optional[bool] = None,
        ignore_https_errors: typing.Optional[bool] = None,
        max_redirects: typing.Optional[int] = None):

        Page.request.delete(url,
        params,
        headers,
        data,
        form,
        multipart,
        timeout,
        fail_on_status_code,
        ignore_https_errors,
        max_redirects)

    def UiPost(self, url: str, *,
              params: typing.Optional[
                  typing.Dict[str, typing.Union[str, float, bool]]
              ] = None,
              headers: typing.Optional[typing.Dict[str, str]] = None,
              data: typing.Optional[typing.Union[typing.Any, bytes, str]] = None,
              form: typing.Optional[typing.Dict[str, typing.Union[str, float, bool]]] = None,
              multipart: typing.Optional[
                  typing.Dict[str, typing.Union[bytes, bool, float, str, FilePayload]]
              ] = None,
              timeout: typing.Optional[float] = None,
              fail_on_status_code: typing.Optional[bool] = None,
              ignore_https_errors: typing.Optional[bool] = None,
              max_redirects: typing.Optional[int] = None):

        self.request.post(url,params,headers,data,
                            form,
                            multipart,
                            timeout,
                            fail_on_status_code,
                            ignore_https_errors,
                            max_redirects)
