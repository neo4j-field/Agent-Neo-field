import * as auth0 from 'auth0-js';
import {getDynamicConfigValue} from "./dynamicConfig";

interface AuthResult {
  expiresIn: number | undefined;
  accessToken: string;
  idToken: string;
  idTokenPayload: Record<string, any>;
}

class Auth {
    private auth0: auth0.WebAuth;
    idTokenPayload: Record<string, unknown>;
    userAccessInfo: Record<string, unknown>;

    constructor() {
        console.log("Initializing Auth0 configuration");
        this.auth0 = new auth0.WebAuth({
            domain: getDynamicConfigValue('REACT_APP_AUTH_DOMAIN')!,
            clientID: getDynamicConfigValue('REACT_APP_AUTH_CLIENT_ID')!, // I don't think I even need this... isn't this if deploying it to hive?
            redirectUri: getDynamicConfigValue('REACT_APP_AUTH_CALLBACK')!,
            responseType: 'token id_token',
            scope: 'openid email profile'
        });
        this.idTokenPayload = {}
        this.userAccessInfo = {}
        this.login = this.login.bind(this);
        this.handleAuthentication = this.handleAuthentication.bind(this);
        this.isAuthenticated = this.isAuthenticated.bind(this);
        this.logout = this.logout.bind(this);
    }

    login() :void {
        console.log("Triggering login");
        this.auth0.authorize({
            prompt: "select_account"
        });
    }
    isAuth0 = () :boolean => getDynamicConfigValue('REACT_APP_AUTH_METHOD') === "auth0";

    getIdToken(): string | null {
    return localStorage.getItem("id_token");
  }

    async handleAuthentication(){
        console.log("Handling authentication");
        const promise = new Promise<void>((resolve, reject) => {
            this.auth0.parseHash(async (err: auth0.Auth0ParseHashError | null, authResult: auth0.Auth0DecodedHash | null) => {
                if (err) {
                    console.error("Error parsing hash", err);
                    return reject(err);
                }
                if (!authResult || !authResult.idToken) {
                    console.error("Invalid authentication result", authResult);
                    return reject(new Error("Invalid authentication result"));
                }
                console.log("Authentication successful, setting session");
                this.setSession(authResult);
                resolve();
            });
        });
        return await promise;
    }
    silentAuth = async (): Promise<boolean> => {
        console.log("Performing silent authentication check");
        return new Promise((resolve, reject) => {
            this.auth0.checkSession({}, (err, authResult?: AuthResult) => {
                if (err) {
                    console.error('Silent authentication error, login required: ', err);
                    reject(err);
                }
                else if (authResult && authResult.idToken) {
                    console.log("Silent authentication successful, updating session");
                    this.setSession(authResult);
                    resolve(true);
                }
                else {
                    console.log("Silent authentication failed, no idToken received");
                    resolve(false);
                }
            });
    });
  };

    setSession(authResult: auth0.Auth0DecodedHash) {
        console.log("Setting session storage with auth results");
        const expiresIn = authResult.expiresIn ?? 3600;
        const expiresAt: number = expiresIn * 1000 + new Date().getTime();

        if (authResult.accessToken) {
            localStorage.setItem('access_token', authResult.accessToken);
        }
        else {
            console.warn('AccessToken is undefined.');
        }

        if (authResult.idToken) {
            localStorage.setItem('id_token', authResult.idToken);
        }
        else {
            console.warn('IdToken is undefined.');
        }

        this.idTokenPayload = authResult.idTokenPayload;

        localStorage.setItem('expires_at', `${expiresAt}`);
        localStorage.setItem('link_idx', '1');

        // Redirect to the home page after successful login
        console.log("Session set, redirecting to home");
        window.location.href = '/';
    }

    removeLocalStorageItems(): void{
        console.log("Clearing local storage items");
        localStorage.remove('user');
        localStorage.remove('access_token');
        localStorage.remove('id_token');
        localStorage.remove('expires_at');
    }

    logout(): void{
        this.removeLocalStorageItems();
        const authDomain = getDynamicConfigValue('REACT_APP_AUTH_DOMAIN' || 'REACT_APP_AUTH_DOMAIN not specified');
        const logoutUrl = getDynamicConfigValue("REACT_APP_AUTH_LOGOUT_URL") || "REACT_APP_AUTH_LOGOUT_URL not specified";
        window.location.replace(`https://${authDomain}/v2/logout/?returnTo=${logoutUrl}`); // do I even need client id here

    }

    isAuthenticated(): boolean {
         console.log("Checking if user is authenticated");
         if (this.isAuth0()) {
            const expiresAt = Number(localStorage.getItem('expires_at') || '0');
            return new Date().getTime() < expiresAt;
        }
        return false;
    }


}

const auth = new Auth();
export default auth;