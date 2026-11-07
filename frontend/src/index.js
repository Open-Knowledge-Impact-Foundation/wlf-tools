import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import reportWebVitals from './reportWebVitals';
import App from "./SuperApp";
import i18n from './i18n';
const isBeta = process.env?.REACT_APP_STAGE?.toLowerCase() === "beta";
let notifiedAboutBeta = true;
if(isBeta && !notifiedAboutBeta){
  alert(
    i18n.t('beta.warning', { defaultValue :  `This is Experimental version. 
      Although this UI is not stable yet and subject to modification, 
      your action CAN UPDATE the data on the server because we are using the same database.
      If you want to go to the latest stable version, please go to tools.wikilovesfolklore.org`})
   )
}
const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals(console.log);
