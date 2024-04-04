import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import auth from './auth';
import { getDynamicConfigValue } from './dynamicConfig';

const Callback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const doAsync = async () => {
      await auth.handleAuthentication({ caller: 'callback' });
      const redirectUrl = getDynamicConfigValue('REACT_APP_HIVE_UI') || '/';
      navigate(redirectUrl);
    };

    doAsync();
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
