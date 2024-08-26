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
        const domain = getDynamicConfigValue('AUTH_DOMAIN')!;
        const clientID = getDynamicConfigValue('AUTH_CLIENT_ID')!;
        const redirectUri = getDynamicConfigValue('AUTH_CALLBACK')!;
        const authMethod = getDynamicConfigValue('AUTH_METHOD');

        console.log("Initializing Auth0 configuration with:");
        console.log(` Domain: ${domain}`);
        console.log(` Client ID: ${clientID}`);
        console.log(` Redirect URI: ${redirectUri}`);
        console.log(` Auth Method: ${authMethod}`);

        this.auth0 = new auth0.WebAuth({
            domain: domain,
            clientID: clientID,
            redirectUri: redirectUri,
            responseType: 'token id_token',
            scope: 'openid email profile'

        });

        this.idTokenPayload = {};
        this.userAccessInfo = {};
        this.login = this.login.bind(this)
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
    isAuth0 = () :boolean => getDynamicConfigValue('AUTH_METHOD') === "auth0";

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
        return new Promise((resolve, reject) => {
            this.auth0.checkSession({}, (err, authResult?: AuthResult) => {
                if (err) {
                    reject(err);
                }
                else if (authResult && authResult.idToken) {
                    this.setSession(authResult);
                    resolve(true);
                }
                else {
                    resolve(false);
                }
            });
    });
  };

    setSession(authResult: auth0.Auth0DecodedHash) {
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


    }

    removeLocalStorageItems(): void{
        localStorage.remove('user');
        localStorage.remove('access_token');
        localStorage.remove('id_token');
        localStorage.remove('expires_at');
    }

    logout(): void{
        this.removeLocalStorageItems();
        const authDomain = getDynamicConfigValue('AUTH_DOMAIN' || 'AUTH_DOMAIN not specified');
        const logoutUrl = getDynamicConfigValue("AUTH_LOGOUT_URL") || "AUTH_LOGOUT_URL not specified";
        window.location.replace(`https://${authDomain}/v2/logout/?returnTo=${logoutUrl}`); // do I even need client id here

    }

    isAuthenticated(): boolean {
        if (this.isAuth0()) {
            const expiresAt = Number(localStorage.getItem('expires_at') || '0');

            const currentTime = new Date().getTime();

            const isAuthenticated = currentTime < expiresAt;

            return isAuthenticated;
    }

    return false;
}


}

const auth = new Auth();
export default auth;