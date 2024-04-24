import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import auth from './auth';
import { getDynamicConfigValue } from './dynamicConfig';

const Callback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const doAsync = async () => {
      await auth.handleAuthentication();
      const redirectUrl = '/';
      navigate(redirectUrl, {replace:true});
  };

  doAsync().catch(error => {
    console.error("Failed to complete authentication process:", error);
  });
  }, [navigate]);

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
