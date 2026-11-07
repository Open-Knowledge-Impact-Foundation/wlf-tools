
import './App.css';
import React from "react";
import * as Sentry from "@sentry/react";
import AppBar from './Layout/AppBar.jsx';
import AppDrawer from './Layout/AppDrawer';
import Footer from './Layout/Footer';
import Server from './Server.ts';
import {
  Route,
  Routes as _Routes,
} from "react-router-dom";
import { FnFRoutes } from './FnF/FnF.jsx';
import { CampWizRoutes } from './CampWiz/CampWiz.jsx';
import { useTranslation } from 'react-i18next';
const FnF = React.lazy(() => import('./FnF/FnF.jsx'));
const CampWiz = React.lazy(() => import('./CampWiz/CampWiz.jsx'));
const LanguageSelector = React.lazy(() => import('./Layout/LanguageSelector.jsx'));
const UserfeedBackForm = React.lazy(() => import('./UserfeedBackForm.jsx'));
const RedirectToLoginPage = () => {
  const callback = encodeURIComponent(window.location.href);
  return <meta httpEquiv="refresh" content={`5; url=/login/?callback=${callback}`} />
}
const Routes = Sentry.withSentryReactRouterV6Routing(_Routes);
export function ToolSelector(t) {
  const url = new URL(window.location.href);
  const tool = url.searchParams.get('tool') || url.pathname.split('/')[1];
  switch (tool) {
    case 'fnf':
      return ['FnF', '/fnf', FnFRoutes]
    case 'campwiz':
      return [t('name'), '/campwiz', CampWizRoutes]
    default:
      return ['FnF', '', FnFRoutes];
  }
}

const Tools = []
function App() {
  const { t } = useTranslation();
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [toolName, toolPath, getRoutes] = ToolSelector(t);
  const [feedbackOpen, setFeedbackOpen] = React.useState(false);
  const [languageOpen, setLanguageOpen] = React.useState(false);
  const user = Server.loginnedUser();
  if (user) {
    // setUser(decoded);
    Tools[0] = getRoutes(user);
    // Tools[1] = CampWizRoutes(decoded);
  } else {
    console.log("Please login to continue", window.location.href);
    return <RedirectToLoginPage />
  }
  const commonProps = {
    user,
    toolName,
    toolPath,
    setOpen: setDrawerOpen,
    open: drawerOpen,
  }
  return (
    <>
      {/* <UserfeedBackForm user={user}  projectId={Sentry.getCurrentHub().getClient().getDsn().projectId} /> */}

      <AppBar {...commonProps} setLanguageOpen={setLanguageOpen} />
      <AppDrawer {...commonProps} components={Tools} setFeedbackOpen={setFeedbackOpen} setLanguageOpen={setLanguageOpen} />
      {languageOpen && <LanguageSelector close={() => setLanguageOpen(false)} />}
      {/* {feedbackOpen && <UserfeedBackForm setFeedbackOpen={setFeedbackOpen} username={user?.username} />} */}
      <Routes>
        <Route path="/fnf/*" element={<FnF {...commonProps} />} title="FnF" />
        <Route path="/campwiz/*" element={<CampWiz {...commonProps} />} title={t('name')} />
      </Routes>
      <Footer />
    </>
  );
}


export default App;
