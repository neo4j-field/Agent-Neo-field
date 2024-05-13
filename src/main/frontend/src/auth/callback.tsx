import React, { useEffect } from 'react';
import auth from './auth';
import { getDynamicConfigValue } from './dynamicConfig';

const Callback = () => {

  useEffect(() => {
    const doAsync = async () => { 
      try {
        await auth.handleAuthentication();
      } catch (e) {
        console.log('error calling handleAuthentication', e);
      }
      const redirectUrl = '/';
      window.location.replace(redirectUrl);
    }
    doAsync();
  }, []);

  const style: React.CSSProperties = {
    position: "absolute",
    display: "flex",
    justifyContent: "center",
    height: "100vh",
    width: "100vw",
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: "white",
  };

  return <div style={style} />;
};

export default Callback;
