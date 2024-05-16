import {FetchOptions} from "../types/types";

const apiBaseURL = 'https://agent-neo-backend-qaiojvs3da-uc.a.run.app';

export const fetchWithAuth = async ({ endpoint, ...options }: FetchOptions): Promise<any> => {
  const idToken = localStorage.getItem('id_token'); // Retrieve the JWT token from localStorage

  const headers = new Headers(options.headers || {});
  headers.append("Authorization", idToken ? `Bearer ${idToken}` : "");

  const response = await fetch(`${apiBaseURL}${endpoint}`, {
    ...options,
    headers,
  });

  const responseData = await response.json();
  if (!response.ok) {
    throw new Error(responseData.message || "Server error");
  }
  return responseData;
};
