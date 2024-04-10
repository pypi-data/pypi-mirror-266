# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

cimport pymsalruntime.CPyMsalRuntime as mrt
from libc.stdint cimport int32_t, int64_t

from libc.stdio cimport printf
from libc.string cimport memcpy

from enum import IntEnum, Enum
import json
from threading import Event

IF UNAME_SYSNAME == "Windows":
    # __stdcall is needed to specify windows .dll calling conventions.
    ctypedef mrt.MSALRUNTIME_ERROR_HANDLE (__stdcall *_string_getter_func)(mrt.MSALRUNTIME_HANDLE* handle, mrt.os_char* buffer, int32_t* bufferSize) nogil
    cdef void __stdcall _MSALRUNTIMEAuthCompletionCallback(mrt.MSALRUNTIME_AUTH_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMEAuthCompletionCallbackInternal(hResponse, callbackData)
    cdef void __stdcall _MSALRUNTIMELogCallback(const mrt.os_char* logMessage, const mrt.MSALRUNTIME_LOG_LEVEL logLevel, void* callbackData) with gil:
        _MSALRUNTIMELogCallbackInternal(logMessage, logLevel, callbackData)
    cdef void  __stdcall _MSALRUNTIMESignOutCompletionCallback(mrt.MSALRUNTIME_SIGNOUT_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMESignOutCompletionCallbackInternal(hResponse, callbackData)
    cdef void  __stdcall _MSALRUNTIMEReadAccountCompletionCallback(mrt.MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMEReadAccountCompletionCallbackInternal(hResponse, callbackData)
    cdef void  __stdcall _MSALRUNTIMEDiscoverAccountsCompletionCallback(mrt.MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMEDiscoverAccountsCompletionCallbackInternal(hResponse, callbackData)

    def get_console_window():
        cdef void* window_handle = NULL
        cdef int64_t mrt_window = 0

        with nogil:
            # There is a bug on new terminal team where GetConsoleWindow didn't return the correct window which result as any UI prompt from WAM/account control will not be correctly parented. 
            # Using GetAncestor to get the ancestor window handle from GetConsoleWindow is a workaround that new terminal team provided.
            # This workaround shouldn't regress existing console apps via command prompt or powershell.
            ga_root = 3 # see https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getancestor for ga_flags
            window_handle = mrt.GetAncestor(mrt.GetConsoleWindow(), ga_root)
            mrt_window = <int64_t> window_handle

        if window_handle is NULL:
            return None
        else:
            return mrt_window

    def get_desktop_window():
        cdef int64_t mrt_window = 0

        with nogil:
            mrt_window = <int64_t> mrt.GetDesktopWindow()

        return mrt_window

    def _get_encoded_bytes(str input_str):
        return input_str.encode('utf-16-le')

    cdef _get_native_string_length(const mrt.os_char* input):
        cdef size_t len = 0
        while len < 65536 and input[len] != 0:
            len += 1
        return len

    cdef _get_decoded_string_from_oschar(const mrt.os_char* input_str):
        tmp_buf_len = _get_native_string_length(input_str) * sizeof(mrt.os_char)
        tmp_buf = bytearray(tmp_buf_len)
        memcpy(<void*><unsigned char*>tmp_buf, <void*>input_str, tmp_buf_len)
        return tmp_buf.decode("utf-16-le")

    cdef _get_decoded_string_from_bytearray(bytearray input_str):
        return input_str.decode("utf-16-le")

ELSE:
    ctypedef mrt.MSALRUNTIME_ERROR_HANDLE (*_string_getter_func)(mrt.MSALRUNTIME_HANDLE* handle, mrt.os_char* buffer, mrt.int32_t* bufferSize) nogil
    cdef void _MSALRUNTIMEAuthCompletionCallback(mrt.MSALRUNTIME_AUTH_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMEAuthCompletionCallbackInternal(hResponse, callbackData)
    cdef void _MSALRUNTIMELogCallback(const mrt.os_char* logMessage, const mrt.MSALRUNTIME_LOG_LEVEL logLevel, void* callbackData) with gil:
        _MSALRUNTIMELogCallbackInternal(logMessage, logLevel, callbackData)
    cdef void  _MSALRUNTIMESignOutCompletionCallback(mrt.MSALRUNTIME_SIGNOUT_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMESignOutCompletionCallbackInternal(hResponse, callbackData)
    cdef void  _MSALRUNTIMEReadAccountCompletionCallback(mrt.MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMEReadAccountCompletionCallbackInternal(hResponse, callbackData)
    cdef void  _MSALRUNTIMEDiscoverAccountsCompletionCallback(mrt.MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE hResponse, void* callbackData) with gil:
        _MSALRUNTIMEDiscoverAccountsCompletionCallbackInternal(hResponse, callbackData)

    # TODO:ADO 2579635 Resolving window handle issues
    def get_console_window():
        return 1

    def get_desktop_window():
        return 1

    def _get_encoded_bytes(str input_str):
        return input_str.encode('utf-8')

    cdef _get_decoded_string_from_oschar(const mrt.os_char* input_str):
        return str(input_str.decode('utf-8'))

    cdef _get_decoded_string_from_bytearray(bytearray input_str):
        return input_str.decode("utf-8")

IF UNAME_SYSNAME == "Darwin":
    def _runloop_run():
        with nogil:
            mrt.MSALRUNTIME_runloop_run()

    def _runloop_stop():
        with nogil:
            mrt.MSALRUNTIME_runloop_stop()

    class MSALRuntimeMacCallbackEvent:
        def set(self) -> None:
            _runloop_stop()

        def wait(self) -> None:
            _runloop_run()

    def _get_MSALRuntime_event():
        return MSALRuntimeMacCallbackEvent()

ELSE:
    def _get_MSALRuntime_event():
        return Event()

class Response_Status(Enum):
    Status_Unexpected = 0
    Status_Reserved = 1
    Status_InteractionRequired = 2
    Status_NoNetwork = 3
    Status_NetworkTemporarilyUnavailable = 4
    Status_ServerTemporarilyUnavailable = 5
    Status_ApiContractViolation = 6
    Status_UserCanceled = 7
    Status_ApplicationCanceled = 8
    Status_IncorrectConfiguration = 9
    Status_InsufficientBuffer = 10
    Status_AuthorityUntrusted = 11
    Status_UserSwitch = 12
    Status_AccountUnusable = 13
    Status_UserDataRemovalRequired = 14
    Status_KeyNotFound = 15
    Status_AccountNotFound = 16
    Status_TransientError = 17
    Status_AccountSwitch = 18
    Status_RequiredBrokerMissing = 19
    Status_DeviceNotRegistered = 20
    Status_FallbackToNativeMsal = 21


class LogLevel(Enum):
    TRACE = 1
    DEBUG = 2
    INFO = 3
    WARNING = 4
    ERROR = 5
    FATAL = 6


def read_account_by_id(
        str accountid not None,
        str correlationId not None,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    encoded_accountid = NativeString()
    cdef mrt.os_char* coerced_account_id = encoded_accountid.get_os_char_string(accountid)
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_ReadAccountByIdAsync(
            coerced_account_id,
            coerced_correlationId,
            _MSALRUNTIMEReadAccountCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def signin(
        int64_t parentWindowHandle,
        MSALRuntimeAuthParameters auth_params not None,
        str correlationId not None,
        str accountHint,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    cdef int64_t castParentWindowHandle = parentWindowHandle
    cdef MSALRuntimeAuthParameters coerced_auth_params = auth_params
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    encoded_accountHint = NativeString()
    cdef mrt.os_char* coerced_accountHint = encoded_accountHint.get_os_char_string("" if not accountHint else accountHint)
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_SignInAsync(
            <mrt.WINDOW_HANDLE> castParentWindowHandle,
            coerced_auth_params._handle,
            coerced_correlationId,
            coerced_accountHint,
            _MSALRUNTIMEAuthCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def signin_silently(
        MSALRuntimeAuthParameters auth_params not None,
        str correlationId not None,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    cdef MSALRuntimeAuthParameters coerced_auth_params = auth_params
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_SignInSilentlyAsync(
            coerced_auth_params._handle,
            coerced_correlationId,
            _MSALRUNTIMEAuthCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def signin_interactively(
        int64_t parentWindowHandle,
        MSALRuntimeAuthParameters auth_params not None,
        str correlationId not None,
        str accountHint,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    cdef int64_t castParentWindowHandle = parentWindowHandle
    cdef MSALRuntimeAuthParameters coerced_auth_params = auth_params
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    encoded_accountHint = NativeString()
    cdef mrt.os_char* coerced_accountHint = encoded_accountHint.get_os_char_string("" if not accountHint else accountHint)
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_SignInInteractivelyAsync(
            <mrt.WINDOW_HANDLE> castParentWindowHandle,
            coerced_auth_params._handle,
            coerced_correlationId,
            coerced_accountHint,
            _MSALRUNTIMEAuthCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def signout_silently(
        str clientId not None,
        str correlationId not None,
        MSALRuntimeAccount account not None,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    encoded_clientId = NativeString()
    cdef mrt.os_char* coerced_clientId = encoded_clientId.get_os_char_string(clientId)
    cdef MSALRuntimeAccount coerced_account = account
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_SignOutSilentlyAsync(
            coerced_clientId,
            coerced_correlationId,
            coerced_account._handle,
            _MSALRUNTIMESignOutCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def discover_accounts(
        str clientId not None,
        str correlationId not None,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    encoded_clientId = NativeString()
    cdef mrt.os_char* coerced_clientId = encoded_clientId.get_os_char_string(clientId)
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_DiscoverAccountsAsync(
            coerced_clientId,
            coerced_correlationId,
            _MSALRUNTIMEDiscoverAccountsCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def acquire_token_silently(
        MSALRuntimeAuthParameters auth_params not None,
        str correlationId not None,
        MSALRuntimeAccount account not None,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    cdef MSALRuntimeAuthParameters coerced_auth_params = auth_params
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    cdef MSALRuntimeAccount coerced_account = account
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_AcquireTokenSilentlyAsync(
            coerced_auth_params._handle,
            coerced_correlationId,
            coerced_account._handle,
            _MSALRUNTIMEAuthCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def acquire_token_interactively(
        int64_t parentWindowHandle,
        MSALRuntimeAuthParameters auth_params not None,
        str correlationId not None,
        MSALRuntimeAccount account not None,
        py_callback not None):
    callback_data = _MSALRuntimeCallBackData(py_callback)
    cdef int64_t castParentWindowHandle = parentWindowHandle
    cdef MSALRuntimeAuthParameters coerced_auth_params = auth_params
    encoded_correlationId = NativeString()
    cdef mrt.os_char* coerced_correlationId = encoded_correlationId.get_os_char_string(correlationId)
    cdef MSALRuntimeAccount coerced_account = account
    cdef void* coerced_callback_data_id = <void*> callback_data.id
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    cdef MSALRuntimeAsyncHandle async_handle = MSALRuntimeAsyncHandle()

    with nogil:
        mrt_error = mrt.MSALRUNTIME_AcquireTokenInteractivelyAsync(
            <mrt.WINDOW_HANDLE> castParentWindowHandle,
            coerced_auth_params._handle,
            coerced_correlationId,
            coerced_account._handle,
            _MSALRUNTIMEAuthCompletionCallback,
            coerced_callback_data_id,
            &async_handle._handle)

    _check_error(mrt_error)
    return async_handle

def register_logging_callback(py_callback not None):
    cdef MSALRuntimeLogCallbackHandle callback_handle = MSALRuntimeLogCallbackHandle()

    callback_data = _MSALRuntimeCallBackData(py_callback)
    cdef void* coerced_callback_data_id = <void*> callback_data.id

    with nogil:
        mrt_error = mrt.MSALRUNTIME_RegisterLogCallback(
            _MSALRUNTIMELogCallback,
            coerced_callback_data_id,
            &callback_handle._handle)

    _check_error(mrt_error)

    # store the callback id in the log callback storage to release later
    _logCallbackStorage[callback_handle] = callback_data.id
    return callback_handle

def set_is_pii_enabled(int32_t enabled):
    with nogil:
        mrt.MSALRUNTIME_SetIsPiiEnabled(enabled)

cdef class MSALRuntimeLogCallbackHandle:
    cdef mrt.MSALRUNTIME_LOG_CALLBACK_HANDLE _handle

    def __cinit__(self):
        self._handle = NULL

    def release_logging_callback(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_ReleaseLogCallbackHandle(self._handle)

        _ignore_error(mrt_error)
        # Remove callback from interop callback storage.
        _callbackStorage.pop(_logCallbackStorage.pop(self))


cdef class MSALRuntimeAsyncHandle:
    cdef mrt.MSALRUNTIME_ASYNC_HANDLE _handle

    def __cinit__(self):
        self._handle = NULL

    def __dealloc__(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        if self._handle:
            with nogil:
                mrt_error = mrt.MSALRUNTIME_ReleaseAsyncHandle(self._handle)

            _ignore_error(mrt_error)

    def cancel_async_operation(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_CancelAsyncOperation(self._handle)

        _check_error(mrt_error)

cdef class MSALRuntimeAccount:
    cdef mrt.MSALRUNTIME_ACCOUNT_HANDLE _handle

    def __cinit__(self, rawHandle not None):
        cdef int64_t castHandle = rawHandle
        self._handle = <mrt.MSALRUNTIME_ACCOUNT_HANDLE> castHandle

    def __dealloc__(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        if self._handle:
            with nogil:
                mrt_error = mrt.MSALRUNTIME_ReleaseAccount(self._handle)

            _ignore_error(mrt_error)

    def get_account_id(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetAccountId, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_home_account_id(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetHomeAccountId, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_environment(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetEnvironment, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_realm(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetRealm, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_local_account_id(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetLocalAccountId, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_user_name(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetUserName, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_given_name(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetGivenName, <mrt.MSALRUNTIME_HANDLE*> self._handle)
        
    def get_family_name(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetFamilyName, <mrt.MSALRUNTIME_HANDLE*> self._handle)     

    def get_middle_name(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetMiddleName, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_display_name(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetDisplayName, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_additional_fields_json(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetAdditionalFieldsJson, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_home_environment(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetHomeEnvironment, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_client_info(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetClientInfo, <mrt.MSALRUNTIME_HANDLE*> self._handle)

cdef class MSALRuntimeAuthParameters:
    cdef mrt.MSALRUNTIME_AUTH_PARAMETERS_HANDLE _handle

    def __init__(self, str clientid not None, str authority not None):
        self._handle = NULL
        encoded_clientid = NativeString()
        cdef mrt.os_char* coerced_clientid = encoded_clientid.get_os_char_string(clientid)
        encoded_authority = NativeString()
        cdef mrt.os_char* coerced_authority = encoded_authority.get_os_char_string(authority)
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_CreateAuthParameters(
                coerced_clientid,
                coerced_authority,
                &self._handle)

        _check_error(mrt_error)

    def __dealloc__(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        if self._handle:
            with nogil:
                mrt_error = mrt.MSALRUNTIME_ReleaseAuthParameters(self._handle)

            _ignore_error(mrt_error)

    def set_requested_scopes(self, scopes not None):
        if not isinstance(scopes, list):
            raise TypeError('scopes must be an list type')
        scopes_list_string = " ".join(scopes)
        encoded_scopes_list_string = NativeString()
        cdef mrt.os_char* coerced_scopes = encoded_scopes_list_string.get_os_char_string(scopes_list_string)
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_SetRequestedScopes(self._handle, coerced_scopes)

        _check_error(mrt_error)

    def set_redirect_uri(self, str redirect_uri not None):
        encoded_redirect_uri = NativeString()
        cdef mrt.os_char* coerced_redirect_uri = encoded_redirect_uri.get_os_char_string(redirect_uri)
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_SetRedirectUri(self._handle, coerced_redirect_uri)

        _check_error(mrt_error)

    def set_decoded_claims(self, str claims not None):
        encoded_claims = NativeString()
        cdef mrt.os_char* coerced_claims = encoded_claims.get_os_char_string(claims)
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_SetDecodedClaims(self._handle, coerced_claims)

        _check_error(mrt_error)

    def set_access_token_to_renew(self, str access_token_to_renew not None):
        encoded_access_token_to_renew = NativeString()
        cdef mrt.os_char* coerced_access_token_to_renew = encoded_access_token_to_renew.get_os_char_string(access_token_to_renew)
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_SetAccessTokenToRenew(self._handle, coerced_access_token_to_renew)

        _check_error(mrt_error)

    def set_pop_params(
            self,
            str http_method not None,
            str uri_host not None,
            str uri_path,
            str nonce):
        encoded_http_method = NativeString()
        cdef mrt.os_char* coerced_http_method = encoded_http_method.get_os_char_string(http_method)
        encoded_uri_host = NativeString()
        cdef mrt.os_char* coerced_uri_host = encoded_uri_host.get_os_char_string(uri_host)
        encoded_uri_path = NativeString()
        cdef mrt.os_char* coerced_uri_path = encoded_uri_path.get_os_char_string("" if not uri_path else uri_path)
        encoded_nonce = NativeString()
        cdef mrt.os_char* coerced_nonce = encoded_nonce.get_os_char_string("" if not nonce else nonce)

        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_SetPopParams(
                self._handle,
                coerced_http_method,
                coerced_uri_host,
                coerced_uri_path,
                coerced_nonce)

        _check_error(mrt_error)

    def set_additional_parameter(self, str key not None, str value not None):
        encoded_key = NativeString()
        cdef mrt.os_char* coerced_key = encoded_key.get_os_char_string(key)
        encoded_value = NativeString()
        cdef mrt.os_char* coerced_value = encoded_value.get_os_char_string(value)
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_SetAdditionalParameter(
                self._handle,
                coerced_key,
                coerced_value)

        _check_error(mrt_error)

cdef class MSALRuntimeAuthResult:
    cdef mrt.MSALRUNTIME_AUTH_RESULT_HANDLE _handle
    def __cinit__(self, rawHandle not None):
        cdef int64_t castHandle = rawHandle
        self._handle = <mrt.MSALRUNTIME_AUTH_RESULT_HANDLE> castHandle

    def __dealloc__(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        if self._handle:
            with nogil:
                mrt_error = mrt.MSALRUNTIME_ReleaseAuthResult(self._handle)

            _ignore_error(mrt_error)

    def get_account(self):
        cdef mrt.MSALRUNTIME_ACCOUNT_HANDLE account_handle = NULL
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetAccount(self._handle, &account_handle)

        _check_error(mrt_error)

        if account_handle == NULL:
            return None

        cdef MSALRuntimeAccount account = MSALRuntimeAccount(<long long> account_handle)
        return account

    def get_id_token(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetIdToken, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_raw_id_token(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetRawIdToken, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_access_token(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetAccessToken, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def get_granted_scopes(self):
        granted_scopes = _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetGrantedScopes, <mrt.MSALRUNTIME_HANDLE*> self._handle)
        if not granted_scopes:
            return None
        return granted_scopes.strip().split(" ")

    def get_authorization_header(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetAuthorizationHeader, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def is_pop_authorization(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
        cdef mrt.bool_t mrt_is_pop_auth = 0

        with nogil:
            mrt_error = mrt.MSALRUNTIME_IsPopAuthorization(
                self._handle,
                &mrt_is_pop_auth)

        _check_error(mrt_error)

        return mrt_is_pop_auth

    def get_authorization_header(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetAuthorizationHeader, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def is_pop_authorization(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
        cdef mrt.bool_t mrt_is_pop_auth = 0

        with nogil:
            mrt_error = mrt.MSALRUNTIME_IsPopAuthorization(
                self._handle,
                &mrt_is_pop_auth)

        _check_error(mrt_error)

        return mrt_is_pop_auth

    def get_authorization_header(self):
        return _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetAuthorizationHeader, <mrt.MSALRUNTIME_HANDLE*> self._handle)

    def is_pop_authorization(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
        cdef mrt.bool_t mrt_is_pop_auth = 0

        with nogil:
            mrt_error = mrt.MSALRUNTIME_IsPopAuthorization(
                self._handle,
                &mrt_is_pop_auth)

        _check_error(mrt_error)

        return mrt_is_pop_auth

    def get_access_token_expiry_time(self):
        cdef int64_t expiry_time = 0
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetExpiresOn(
                self._handle,
                &expiry_time)

        _check_error(mrt_error)
        return <int> expiry_time

    def get_error(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE error_handle = NULL
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetError(self._handle, &error_handle)

        _check_error(mrt_error)

        if error_handle == NULL:
            return None

        cdef MSALRuntimeError msalruntime_error = MSALRuntimeError()
        msalruntime_error._handle = error_handle
        return msalruntime_error

    def get_telemetry_data(self):
        json_py_string = _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetTelemetryData, <mrt.MSALRUNTIME_HANDLE*> self._handle)
        if not json_py_string:
            return None
        return json.loads(json_py_string)

cdef class MSALRuntimeSignOutResult:
    cdef mrt.MSALRUNTIME_SIGNOUT_RESULT_HANDLE _handle
    def __cinit__(self, rawHandle not None):
        cdef int64_t castHandle = rawHandle
        self._handle = <mrt.MSALRUNTIME_SIGNOUT_RESULT_HANDLE> castHandle

    def __dealloc__(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        if self._handle:
            with nogil:
                mrt_error = mrt.MSALRUNTIME_ReleaseSignOutResult(self._handle)

            _ignore_error(mrt_error)

    def get_error(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE error_handle = NULL
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetSignOutError(self._handle, &error_handle)

        _check_error(mrt_error)

        if error_handle == NULL:
            return None

        cdef MSALRuntimeError msalruntime_error = MSALRuntimeError()
        msalruntime_error._handle = error_handle
        return msalruntime_error

    def get_telemetry_data(self):
        json_py_string = _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetSignOutTelemetryData, <mrt.MSALRUNTIME_HANDLE*> self._handle)
        if not json_py_string:
            return None
        return json.loads(json_py_string)

cdef class MSALRuntimeReadAccountResult:
    cdef mrt.MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE _handle
    def __cinit__(self, rawHandle not None):
        cdef int64_t castHandle = rawHandle
        self._handle = <mrt.MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE> castHandle

    def __dealloc__(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
        if self._handle:
            with nogil:
                mrt_error = mrt.MSALRUNTIME_ReleaseReadAccountResult(self._handle)

            _ignore_error(mrt_error)

    def get_account(self):
        cdef mrt.MSALRUNTIME_ACCOUNT_HANDLE account_handle = NULL
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetReadAccount(self._handle, &account_handle)

        _check_error(mrt_error)

        if account_handle == NULL:
            return None

        cdef MSALRuntimeAccount account = MSALRuntimeAccount(<long long> account_handle)
        return account

    def get_error(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE error_handle = NULL
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetReadAccountError(self._handle, &error_handle)

        _check_error(mrt_error)

        if error_handle == NULL:
            return None

        cdef MSALRuntimeError msalruntime_error = MSALRuntimeError()
        msalruntime_error._handle = error_handle
        return msalruntime_error

    def get_telemetry_data(self):
        json_py_string = _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetReadAccountTelemetryData, <mrt.MSALRUNTIME_HANDLE*> self._handle)
        if not json_py_string:
            return None
        return json.loads(json_py_string)

cdef class MSALRuntimeDiscoverAccountsResult:
    cdef mrt.MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE _handle
    cdef list _accounts
    cdef bint _accounts_filled
    def __cinit__(self, rawHandle not None):
        cdef int64_t castHandle = rawHandle
        self._handle = <mrt.MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE> castHandle
        self._accounts = []
        self._accounts_filled = False

    def __dealloc__(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        self._accounts.clear()

        if self._handle:
            with nogil:
                mrt_error = mrt.MSALRUNTIME_ReleaseDiscoverAccountsResult(self._handle)

            _ignore_error(mrt_error)

    def get_accounts(self):
        cdef mrt.MSALRUNTIME_ACCOUNT_HANDLE account_handle = NULL
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
        cdef int32_t index = 0

        if not self._accounts_filled:
            while True:
                with nogil:
                    mrt_error = mrt.MSALRUNTIME_GetDiscoverAccountsAt(self._handle, index, &account_handle)

                _check_error(mrt_error)

                if account_handle == NULL:
                    self._accounts_filled = True
                    break

                account = MSALRuntimeAccount(<long long> account_handle)
                self._accounts.append(account)

                index += 1
        return self._accounts

    def get_error(self):
        cdef mrt.MSALRUNTIME_ERROR_HANDLE error_handle = NULL
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetDiscoverAccountsError(self._handle, &error_handle)

        _check_error(mrt_error)

        if error_handle == NULL:
            return None

        cdef MSALRuntimeError msalruntime_error = MSALRuntimeError()
        msalruntime_error._handle = error_handle
        return msalruntime_error

    def get_telemetry_data(self):
        json_py_string = _get_string(<_string_getter_func> mrt.MSALRUNTIME_GetDiscoverAccountsTelemetryData, <mrt.MSALRUNTIME_HANDLE*> self._handle)
        if not json_py_string:
            return None
        return json.loads(json_py_string)

cdef class MSALRuntimeError:
    cdef mrt.MSALRUNTIME_ERROR_HANDLE _handle
    def __cinit__(self):
        self._handle = NULL

    def __dealloc__(self):
        if self._handle:
            with nogil:
                # MSALRUNTIME_ReleaseError returns bool_t
                mrt.MSALRUNTIME_ReleaseError(self._handle)

    def get_status(self):
        cdef mrt.MSALRUNTIME_RESPONSE_STATUS status
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetStatus(self._handle, &status)
        _raise_if_error(mrt_error, "get_status")

        return Response_Status(<int> status)

    def get_error_code(self):
        cdef int64_t error_code = 0
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetErrorCode(self._handle, &error_code)
        _raise_if_error(mrt_error, "get_error_code")

        return error_code

    def get_tag(self):
        cdef int32_t tag = 0
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

        with nogil:
            mrt_error = mrt.MSALRUNTIME_GetTag(self._handle, &tag)
        _raise_if_error(mrt_error, "get_tag")

        return tag

    def get_context(self):
        cdef NativeString nstr = NativeString()
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_first_error = NULL
        cdef MSALRuntimeError msalruntime_error = MSALRuntimeError()

        with nogil:
            mrt_first_error = mrt.MSALRUNTIME_GetContext(
                self._handle,
                NULL,
                &nstr.buffer_size)

        if mrt_first_error:
            msalruntime_error._handle = mrt_first_error
            errorStatus = msalruntime_error.get_status();
            if (errorStatus != Response_Status(<int> mrt.MSALRUNTIME_RESPONSE_STATUS.Msalruntime_Response_Status_InsufficientBuffer)):
                raise RuntimeError("Get Context return unexpected status: %s" % Response_Status(errorStatus))

        if nstr.is_empty():
            return None

        cdef mrt.os_char* coerced_buffer = nstr.allocate()
        cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_second_error = NULL

        with nogil:
            mrt_second_error = mrt.MSALRUNTIME_GetContext(
                self._handle,
                coerced_buffer,
                &nstr.buffer_size)

        _raise_if_error(mrt_second_error, "get_context")
        return nstr.get_string()

# Error helper functions
cdef _raise_if_error(mrt.MSALRUNTIME_ERROR_HANDLE error, name):
    cdef MSALRuntimeError msalruntime_error = MSALRuntimeError()

    if error:
        # assign the handle to the error for proper clean up
        msalruntime_error._handle = error
        # Raise generic error to prevent recursively getting error properties.
        raise RuntimeError("%s return unexpected" % name)

cdef _ignore_error(mrt.MSALRUNTIME_ERROR_HANDLE error):
    if error:
        # Release the error for proper clean up
        mrt.MSALRUNTIME_ReleaseError(error)

cdef _check_error(mrt.MSALRUNTIME_ERROR_HANDLE error, expected_status=None):
    cdef MSALRuntimeError msalruntime_error = MSALRuntimeError()

    if error:
        msalruntime_error._handle = error
        errorStatus = msalruntime_error.get_status();
        if (errorStatus == expected_status):
            return

        errorCode = msalruntime_error.get_error_code()
        errorTag = msalruntime_error.get_tag();
        errorContext = msalruntime_error.get_context()

        raise RuntimeError("ErrorTag: %d, ErrorCode: %d, ErrorContext: %s, ErrorStatus: %s" % (errorTag, errorCode, errorContext, Response_Status(errorStatus)))

# Private startup/shutdown functions which pin/unpin the .dll
def _startup_msalruntime():
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL
    with nogil:
        mrt_error = mrt.MSALRUNTIME_Startup()

    _check_error(mrt_error)

def _shutdown_msalruntime():
    # clean up any remaining log callbacks (copy here is needed as map is modified in this op)
    handle_storage = list(_logCallbackStorage.keys())
    for log_callback_handle in handle_storage:
        log_callback_handle.release_logging_callback()

    with nogil:
        mrt.MSALRUNTIME_Shutdown()

# String helper functions
cdef class NativeString:
    cdef int32_t buffer_size
    cdef bytearray buffer

    def __cinit__(self):
        self.buffer_size = 0

    cdef mrt.os_char* get_os_char_string(self, str py_str):
        bytes_object = _get_encoded_bytes(py_str)
        self.buffer_size = len(bytes_object) // sizeof(mrt.os_char) + 1
        self.buffer = bytearray(self.buffer_size * sizeof(mrt.os_char))
        for i in range(len(bytes_object)):
            self.buffer[i] = bytes_object[i]
        return <mrt.os_char*><unsigned char*> self.buffer

    cdef mrt.os_char* allocate(self):
        self.buffer = bytearray(self.buffer_size * sizeof(mrt.os_char))
        return <mrt.os_char*><unsigned char*> self.buffer

    def get_string(self):
        return _get_decoded_string_from_bytearray(self.buffer[:(self.buffer_size - 1) * sizeof(mrt.os_char)])

    def is_empty(self):
        return self.buffer_size == 0

cdef str _get_string(_string_getter_func func, mrt.MSALRUNTIME_HANDLE* handle):
    cdef NativeString nstr = NativeString()
    cdef mrt.MSALRUNTIME_ERROR_HANDLE mrt_error = NULL

    with nogil:
        mrt_error = func(
            handle,
            NULL,
            &nstr.buffer_size)

    _check_error(mrt_error, expected_status=Response_Status(<int> mrt.MSALRUNTIME_RESPONSE_STATUS.Msalruntime_Response_Status_InsufficientBuffer))

    if nstr.is_empty():
        return None

    cdef mrt.os_char* coerced_buffer = nstr.allocate()

    with nogil:
        mrt_error = func(
            handle,
            coerced_buffer,
            &nstr.buffer_size)

    _check_error(mrt_error)
    return nstr.get_string()
# Callback helper functions
_callbackStorage = {}

cdef void  _MSALRUNTIMEAuthCompletionCallbackInternal(mrt.MSALRUNTIME_AUTH_RESULT_HANDLE hResponse, void* callbackData) with gil:
    callbackId = <object> callbackData

    callback_data = _callbackStorage.pop(callbackId, None)
    if callback_data:
        if (hResponse == NULL):
            raise RuntimeError("Auth callback result handle is NULL")

        callback_data.callback(MSALRuntimeAuthResult(<long long> hResponse))

cdef void  _MSALRUNTIMESignOutCompletionCallbackInternal(mrt.MSALRUNTIME_SIGNOUT_RESULT_HANDLE hResponse, void* callbackData) with gil:
    callbackId = <object> callbackData

    callback_data = _callbackStorage.pop(callbackId, None)
    if callback_data:
        if (hResponse == NULL):
            raise RuntimeError("SignOut callback result handle is NULL")

        callback_data.callback(MSALRuntimeSignOutResult(<long long> hResponse))

cdef void  _MSALRUNTIMEReadAccountCompletionCallbackInternal(mrt.MSALRUNTIME_READ_ACCOUNT_RESULT_HANDLE hResponse, void* callbackData) with gil:
    callbackId = <object> callbackData

    callback_data = _callbackStorage.pop(callbackId, None)
    if callback_data:
        if (hResponse == NULL):
            raise RuntimeError("ReadAccount callback result handle is NULL")

        callback_data.callback(MSALRuntimeReadAccountResult(<long long> hResponse))

cdef void  _MSALRUNTIMEDiscoverAccountsCompletionCallbackInternal(mrt.MSALRUNTIME_DISCOVER_ACCOUNTS_RESULT_HANDLE hResponse, void* callbackData) with gil:
    callbackId = <object> callbackData

    callback_data = _callbackStorage.pop(callbackId, None)
    if callback_data:
        if (hResponse == NULL):
            raise RuntimeError("Callback result handle is NULL")

        callback_data.callback(MSALRuntimeDiscoverAccountsResult(<long long> hResponse))

class _MSALRuntimeCallBackData:
    def __init__(self, callback):
        self.callback = callback
        self.id = id(self)

        _callbackStorage[self.id] = self

# Log Callback helper functions
_logCallbackStorage = {}
cdef void _MSALRUNTIMELogCallbackInternal(const mrt.os_char* logMessage, const mrt.MSALRUNTIME_LOG_LEVEL mrtLogLevel, void* callbackData) with gil:
    callbackId = <object> callbackData

    # create deep copy of logMessage
    py_string = _get_decoded_string_from_oschar(logMessage)
    callback_data = _callbackStorage.get(callbackId, None)
    if callback_data:
        callback_data.callback(py_string, LogLevel(mrtLogLevel))

class CallbackData:
    def __init__(self, is_interactive=False):
        if is_interactive:
            self.signal = _get_MSALRuntime_event()
        else:
            self.signal = Event()
        self.result = None

    def complete(self, result):
        self.result = result
        self.signal.set()
