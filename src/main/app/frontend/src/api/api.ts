import {FetchOptions} from "../types/types";



export const fetchWithAuth = async ({ endpoint, ...options }: FetchOptions): Promise<any> => {
  const idToken = localStorage.getItem('id_token');

  const headers = new Headers(options.headers || {});
  headers.append("Authorization", idToken ? `Bearer ${idToken}` : "");
  const response = await fetch(`${import.meta.env.VITE_BACKEND_DEV_ADDRESS}/llm`, {
    ...options,
    headers,
  });

  const responseData = await response.json();


  if (!response.ok) {
    throw new Error(responseData.message || "Server error");
  }
  return responseData;
};
