import {  Paper, Typography } from "@mui/material";

import Server from "../Server";
import Footer from "../../Layout/Footer";
import { useEffect, useState } from "react";
import CampaignList from "./Campaign";
import { useTranslation } from "react-i18next";

export default function Description({ user }) {

    const {t} = useTranslation();
    const [banner, setBanner] = useState('');
    useEffect(() => {
        Server.getConfig().then((res) => {
            if (res?.campwiz?.dashboard?.banner)
                setBanner(res.campwiz.dashboard.banner);
        }
        ).catch((err) => {
            console.log(err);
        });
    }, []);
    // if(Server.hasAccess(user.rights, Server.RIGHTS.TASK))
    //     sections.push(
    //         <Box key="task" sx={{ display: 'flex', flexDirection: 'row', p: 1, alignItems: 'center', justifyContent: 'center' }} component="fieldset">
    //         <legend>List Generation</legend>
    //         <Button variant="contained" color="primary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/task/create"
    //         >
    //             <AddIcon /> &nbsp; Add Task
    //         </Button>
    //         <Button variant="contained" color="secondary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/task"
    //         >
    //             <ListIcon /> &nbsp; List Tasks
    //         </Button>
    //     </Box>
    //     );
    // if(Server.hasAccess(user.rights, Server.RIGHTS.TOPIC))
    //     sections.push(
    //         <Box key="topic" sx={{ display: 'flex', flexDirection: 'row', p: 1, alignItems: 'center', justifyContent: 'center' }} component="fieldset">
    //         <legend>Topic Management</legend>
    //         <Button variant="contained" color="primary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/topic/create"
    //         >
    //             <AddIcon /> &nbsp; Create New Topic
    //         </Button>
    //         <Button variant="contained" color="secondary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/topic"
    //         >
    //             <ListIcon /> &nbsp; See All Topics
    //         </Button>
    //     </Box>
    //     );
    // sections.push(
    //     <Box key="campaign" sx={{ display: 'flex', flexDirection: 'row', p: 1, alignItems: 'center', justifyContent: 'center' }} component="fieldset">
    //         <legend>Campaign Management</legend>
    //         <Button variant="contained" color="primary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/campaign/new"
    //         >
    //             <AddIcon /> &nbsp; Create New Campaign
    //         </Button>
    //         <Button variant="contained" color="secondary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/campaign"
    //         >
    //             <ListIcon /> &nbsp; See All Campaigns
    //         </Button>
    //     </Box>
    // );
    // sections.push(
    //     <Box key="user" sx={{ display: 'flex', flexDirection: 'row', p: 1, alignItems: 'center', justifyContent: 'center' }} component="fieldset">
    //         <legend>User Management</legend>
    //         <Button variant="contained" color="primary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/setting"
    //         >
    //             <SettingIcon /> &nbsp; Settings
    //         </Button>
    //         {(Server.hasAccess(user.rights, Server.RIGHTS.STATS) || Server.hasAccess(user.rights, Server.RIGHTS.GRANT) ) && 
    //         <Button variant="contained" color="secondary" size="small" sx={{
    //             padding: 1,
    //             m: 1
    //         }}
    //             component={Link}
    //             to="/campwiz/user"
    //         >
    //             <PeopleIcon /> &nbsp; See All Users
    //         </Button>}
    //     </Box>
    // );
    return (
        <Paper sx={{
            // height: "100%",
            width: "100%",
            m: 0,
            border: 0,
            outline: 0,
            position: 'absolute',
            textAlign: 'center',
        }}>
            {banner != '' && <img src={banner} style={{ maxHeight: '150px', maxWidth: '99%' }} />}
            <Typography variant="title" component="h2" sx={{
                textAlign: 'center',
                m: 2
            }}>
                {t("dashboard.welcome", {username: user?.username})}
            </Typography>
            <Typography sx={{ mb: 1, textAlign: 'center', p: 1, pb: 2, display: 'block', overflow: 'hidden' }} color="text.secondary">
                {t('dashboard.description')}
            </Typography>
            <CampaignList />
            <Footer />
        </Paper>
    )
}
