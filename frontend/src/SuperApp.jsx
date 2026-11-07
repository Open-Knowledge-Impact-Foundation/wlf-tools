import { ThemeProvider } from "@mui/material";
import React from "react";
import { useTranslation } from "react-i18next";
import { BrowserRouter, Route, Routes as _Routes, createRoutesFromChildren, matchRoutes, useLocation, useNavigationType } from "react-router-dom";
import * as Sentry from "@sentry/react";
import theme from './Layout/theme';
import LoadingPage from "./Layout/LoadingPage.jsx";



const App = React.lazy(() => import('./App.jsx'));

const dsn = "https://d5f72a7651486fb43aef6fded21f5385@o249367.ingest.sentry.io/4506264792727552";
Sentry.init({
    dsn: dsn,
    environment: process.env.NODE_ENV || 'development',
    beforeSend(event, hint) {
        //prevent reporting of errors from development
        if (process.env.NODE_ENV !== 'production') {
            return null;
        }
        // Check if it is an exception, and if so, show the report dialog
        if (event.exception) {
            Sentry.showReportDialog({ eventId: event.event_id, labelEmail: "Wikipedia Username", labelName: "Name", });
        }
        return event;

    },
    integrations: [
        new Sentry.BrowserProfilingIntegration(),
        new Sentry.BrowserTracing({
            // Set 'tracePropagationTargets' to control for which URLs distributed tracing should be enabled
            tracePropagationTargets: ["localhost:3000", /^https:\/\/tools\.wikilovesfolklore\.org/],
        }),
        new Sentry.Replay(
            {
                networkDetailAllowUrls: [window.location.origin],
            }
        ),
    ],
    routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes
    ),
    // Performance Monitoring
    tracesSampleRate: 0.8, // Capture 100% of the transactions
    // Session Replay
    replaysSessionSampleRate: 0.05, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
    replaysOnErrorSampleRate: 1, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
});


const Routes = Sentry.withSentryReactRouterV6Routing(_Routes);
const SuperApp = () => {
    const { t } = useTranslation();
    return (
        <Sentry.ErrorBoundary fallback={<div>{t("error.unknown")}</div>} showDialog>
            <ThemeProvider theme={theme}>
                <BrowserRouter>
                    <React.Suspense fallback={<LoadingPage />}>
                        <Routes>
                            <Route path='/'>
                                <Route path="*" element={<App />} />
                            </Route>
                        </Routes>
                    </React.Suspense>
                </BrowserRouter>
            </ThemeProvider>
        </Sentry.ErrorBoundary>
    )
}
export default SuperApp;