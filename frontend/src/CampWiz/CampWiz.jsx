import { Routes as _Routes, Route } from "react-router-dom"
import React, { lazy, useEffect } from "react"
import CampWizServer from "./Server.ts"
import "./index.css"
import CampaignIcon from '@mui/icons-material/Campaign';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import Dashboard from "./Pages/Dashboard.jsx"
import ArticleSubmissionPage from "./Pages/Campaign/Submission/NewSubmission.jsx"
import SupervisedUserCircleIcon from '@mui/icons-material/SupervisedUserCircle';
import CampaignList from "./Pages/Campaign/index.jsx";
import { withSentryReactRouterV6Routing } from "@sentry/react";
import PeopleIcon from '@mui/icons-material/People';
import LanguageStatistics from "./Pages/Statistics/LanguageStatistics.jsx";
import ManageAccountsIcon from '@mui/icons-material/ManageAccounts';
import { useTranslation } from "react-i18next";

const Routes = withSentryReactRouterV6Routing(_Routes);
const JudgeSubmission = lazy(() => import("./Pages/Campaign/Submission/JudgeSubmission.jsx"))
const SubmissionList = lazy(() => {
    const isBeta = process.env?.REACT_APP_STAGE?.toLowerCase() === "beta";
    if (isBeta) {
        console.log("Switching to Test Version");
        return import("./Pages/Campaign/Submission/index3.jsx")
    }
    else
        return import("./Pages/Campaign/Submission/index3.jsx")
});
const Campaign = lazy(() => import("./Pages/Campaign/Campaign.jsx"));
const CampaignEdit = lazy(() => import("./Pages/Campaign/Configure/Edit.jsx"));
const CampaignCreate = lazy(() => import("./Pages/Campaign/Configure/Create.jsx"));
const ListUser = lazy(() => import("./Pages/User/ListUser.jsx"));
const EditUser = lazy(() => import("./Pages/User/EditUser.jsx"));
const YearStatistics = lazy(() => import("./Pages/Statistics/YearStatistics.jsx"));
const Translator = lazy(() => import("./Pages/Translation/index.jsx"));
await CampWizServer.init();
const RedirectToLoginPage = ({ returnTo }) => {
    return <meta http-equiv="refresh" content={`0; url=/login/?return=${returnTo}`} />
}
const CampWiz = ({ user }) => {
    const { t } = useTranslation();
    useEffect(() => {
        document.title = t('name');
    }, [t]);
    if (!user)
        return <RedirectToLoginPage returnTo={window.location.pathname} />;
    const CampaignRoutes = (
        <Route path='campaign'>
            <Route path=":campaignID">
                <Route path="submission" >
                    <Route path="new" element={<ArticleSubmissionPage />} />
                    <Route path=":submissionID" element={<JudgeSubmission />} />
                    <Route path="" element={<SubmissionList />} />
                </Route>
                <Route path="edit" element={<CampaignEdit />} />
                <Route path="" element={<Campaign />} />
            </Route>
            <Route path="new" element={<CampaignCreate />} />
            <Route path="" element={<CampaignList />} />
        </Route>
    );
    const UserRoutes = (
        <Route path='user/*'>
            <Route path="edit" element={<EditUser user={user} />} />
            <Route path="*" element={<ListUser user={user} />} />
        </Route>
    )
    return (
        <Routes>
            {CampaignRoutes}
            {CampWizServer.hasAccess(user.rights, CampWizServer.RIGHTS.GRANT) && UserRoutes}
            <Route path="statistics/*">
                <Route path=":campaignID" element={<LanguageStatistics user={user} />} />
                <Route path="*" element={<YearStatistics user={user} />} />
            </Route>
            <Route path="translate" element={<Translator user={user} />} />
            <Route path="*" element={<Dashboard user={user} />} />
        </Routes>
    )
}
const CampWizUserRoutes = {
    name: 'users',
    icon: <PeopleIcon />,
    path: '/campwiz/user',
    children: [
        {
            name: 'Edit',
            icon: <ManageAccountsIcon />,
            path: '/campwiz/user/:id/edit'
        },
        {
            name: 'List',
            icon: <SupervisedUserCircleIcon />,
            path: '/campwiz/user'
        }
    ]
};
export const CampWizRoutes = (user) => {
    const routes = {
        name: 'name',
        icon: null,
        path: '/campwiz',
        children: [
            {
                name: 'campaign',
                icon: <CampaignIcon />,
                path: '/campwiz/campaign',
                children: []
            },
            {
                name: 'statistics',
                icon: <AutoGraphIcon />,
                path: '/campwiz/statistics',
                children: []
            },
        ]
    }
    if (CampWizServer.hasAccess(user.rights, CampWizServer.RIGHTS.GRANT))
        routes.children.push(CampWizUserRoutes)
    return routes;
}
export default CampWiz
