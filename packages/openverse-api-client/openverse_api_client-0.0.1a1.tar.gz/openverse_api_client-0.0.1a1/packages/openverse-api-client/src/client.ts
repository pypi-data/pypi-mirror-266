import { RestAPI, RestAPIMeta } from "./types";

export interface Response<Body> {
    body: Body;
    meta: {
        headers: Headers;
        status: number;
        url: string;
        request: RequestInit;
    };
}

export interface ClientOptions {
    baseUrl?: string;
    credentials?: {
        clientId: string;
        clientSecret: string;
    };
}

/**
 * Get the timestamp as the number of seconds from the UNIX epoch.
 * @returns the UNIX timestamp with a resolution of one second
 */
const currTimestamp = (): number => Math.floor(Date.now() / 1e3);
export const expiryThreshold = 5; // seconds

type OpenverseRequestInit<T extends keyof RestAPI> = {
    headers?: HeadersInit;
} & (RestAPI[T]["params"] extends null ? {} : { params: RestAPI[T]["params"] });

async function getFetch() {
    // Use `globalThis` for node/browser interop
    // Allows users to avoid `cross-fetch` if they don't want it by polyfilling `global.fetch` in non-browser settings
    // @ts-ignore
    if (globalThis.fetch) {
        return {
            fetch,
            Headers: Headers,
        };
    } else {
        return import("cross-fetch").then((d) => ({
            fetch: d.default,
            Headers: d.Headers,
        }));
    }
}

export type OpenverseClient = ReturnType<typeof OpenverseClient>;
export const OpenverseClient = ({
    baseUrl = "https://api.openverse.engineering/",
    credentials,
}: ClientOptions = {}) => {
    let apiToken: RestAPI["POST v1/auth_tokens/token/"]["response"] | null =
        null;

    const apiTokenMutex = {
        requesting: false,
    };

    let tokenExpiry: number | null = null;

    const normalisedBaseUrl = baseUrl.endsWith("/") ? baseUrl : `${baseUrl}/`;

    const baseRequest = async <T extends keyof RestAPI>(
        endpoint: T,
        { headers, ...req }: OpenverseRequestInit<T>
    ): Promise<Response<RestAPI[T]["response"]>> => {
        let [method, url] = endpoint.split(" ");
        const endpointMeta = RestAPIMeta[endpoint];

        const params =
            "params" in req ? { ...(req.params as Record<string, any>) } : {};
        endpointMeta.pathParams.forEach((param) => {
            url = url.replace(`:${param}`, params[param]);
            delete params[param];
        });

        const { fetch, Headers } = await getFetch();

        const finalHeaders = new Headers(headers);
        if (!finalHeaders.has("content-type")) {
            finalHeaders.set("content-type", endpointMeta.contentType);
        }

        const requestConfig: RequestInit = {
            method,
            headers: finalHeaders,
        };

        if (method === "POST") {
            if (finalHeaders.get("content-type") == "application/json") {
                requestConfig["body"] = JSON.stringify(params);
            } else {
                const form = new FormData();
                Object.keys(params).forEach((key) => {
                    form.set(key, params[key]);
                });
                requestConfig["body"] = form;
            }
        } else {
            const search = new URLSearchParams(params);
            if (search.size != 0) {
                url = `${url}?${search}`;
            }
        }

        const fullUrl = `${normalisedBaseUrl}${url}`;
        const response = await fetch(fullUrl, requestConfig);

        const body = endpointMeta.jsonResponse
            ? await response.json()
            : response.body;
        return {
            body: body as RestAPI[T]["response"],
            meta: {
                headers: response.headers,
                status: response.status,
                url: fullUrl,
                request: requestConfig,
            },
        };
    };

    const cannotProceedWithoutToken = () =>
        credentials &&
        (!(apiToken && tokenExpiry) || tokenExpiry <= currTimestamp());

    const shouldTriggerTokenRefresh = () =>
        credentials &&
        !apiTokenMutex.requesting &&
        (!(apiToken && tokenExpiry) ||
            tokenExpiry - expiryThreshold < currTimestamp());

    const refreshApiToken = async () => {
        apiTokenMutex.requesting = true;
        try {
            const tokenResponse = await baseRequest(
                "POST v1/auth_tokens/token/",
                {
                    params: {
                        grant_type: "client_credentials",
                        client_id: (
                            credentials as Exclude<
                                typeof credentials,
                                undefined
                            >
                        ).clientId,
                        client_secret: (
                            credentials as Exclude<
                                typeof credentials,
                                undefined
                            >
                        ).clientSecret,
                    },
                }
            );
            tokenExpiry = currTimestamp() + tokenResponse.body.expires_in;

            apiToken = tokenResponse.body;
        } catch (e) {
            console.error("[openverse-api-client]: Token refresh failed!", e);
        }
        apiTokenMutex.requesting = false;
    };

    const awaitApiToken = async () => {
        while (apiTokenMutex.requesting) {
            await new Promise((res) => setTimeout(res, 300));
        }
    };

    const getAuthHeaders = async (headers: HeadersInit): Promise<Headers> => {
        if (!credentials) {
            return new Headers(headers);
        }

        if (shouldTriggerTokenRefresh()) {
            refreshApiToken();
        }

        if (cannotProceedWithoutToken()) {
            await awaitApiToken();
        }

        const withAuth = new Headers(headers);

        withAuth.append(
            "Authorization",
            `Bearer ${(apiToken as Exclude<typeof apiToken, null>).access_token}`
        );
        return withAuth;
    };

    const request = async <T extends keyof RestAPI>(
        endpoint: T,
        req?: OpenverseRequestInit<T>
    ): Promise<Response<RestAPI[T]["response"]>> => {
        const authHeaders = await getAuthHeaders(req?.headers ?? {});
        return baseRequest(endpoint, {
            ...(req ?? {}),
            headers: authHeaders,
        } as OpenverseRequestInit<T>);
    };

    return request;
};
