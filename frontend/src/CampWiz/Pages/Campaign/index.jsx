import { Route, Routes } from "react-router";
import { lazy, useEffect, useState } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { Autocomplete, Box, Button, TextField, Typography } from "@mui/material";
import CampWizServer from "../../Server";
import SearchIcon from '@mui/icons-material/Search';
import { Link } from "react-router-dom";
import { CreateButton } from "../../Components/CampaignButtons";
import { useTranslation } from "react-i18next";
// import Footer from "../../Components/Footer";
const wiki = CampWizServer.getWikiList();
const CampaignFilter = ({ filter, setFilter }) => {
    const {t} = useTranslation();
    const [language, setLanguage] = useState(filter.language)
    const [status, setStatus] = useState(filter.status);
    return (
        <Box 
        component="div"
        sx={{
            display: 'flex',
            flexDirection: {
                xs: 'column',
                sm: 'row'
            },
            width: '90%',
            justifyContent: 'center',
            alignItems: 'center',
        }}>
            <Autocomplete
                disablePortal
                id="article-name"
                options={wiki}
                size="small"
                // loading={false}
                value={language}
                onChange={(e, v) => setLanguage(v?.id || '')}
                sx={{
                    minWidth: 200,
                    m : 1,
                    width : {
                        xs: '80%',
                        sm: 'auto'
                    }
                }}
                renderInput={(params) => <TextField {...params} label={t('campaign.language')} />}
            />
            <Autocomplete
                disablePortal
                id="article-name"
                options={[ 'pending', 'scheduled', 'running', 'evaluating', 'cancelled', 'rejected', 'ended']}
                size="small"
                multiple
                loading={false}
                value={status}
                onChange={(e, v) => setStatus(v)}
                sx={{
                    minWidth: 200,
                    m : 1,
                    width : {
                        xs: '80%',
                        sm: 'auto'
                    }
                }}
                renderInput={(params) => <TextField {...params} label={t('campaign.status')} />}
            />
            <Button variant="contained" color="primary" size="small" sx={{
                padding: 1,
                m: 1,
                width : {
                    xs: '80%',
                    sm: 'auto'
                }
            }}
                onClick={() => setFilter({ language, status })}
            >
                <SearchIcon /> {t('campaign.action.search')}
            </Button>
        </Box>
    )

}
const CampaignList = () => {
    const {t} = useTranslation();
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState({
        language: '',
        status: ['running', 'scheduled', 'evaluating']

    })
    useEffect(() => {
        (async () => {
            setLoading(true);
            const campaigns = await CampWizServer.Campaign.getCampaigns(filter);
            var serial = 1;
            setCampaigns(campaigns.map(c => ({ ...c, serial : serial++ })));
            setLoading(false);
        })();
    }, [filter]);
    return (
        <div>
            <div style={{ textAlign: 'center' }}>
                <CreateButton />
            </div>
            <Typography variant='h5' sx={{ textAlign: 'center', m: 2 }}>
                {t('campaign.activeCampaigns')}
            </Typography>
            <CampaignFilter filter={filter} setFilter={setFilter} />
            <DataGrid
                loading={loading}
                rows={campaigns}
                autoHeight
                disableColumnMenu
                sx={{
                    '& .MuiDataGrid-columnHeaderTitle': {
                        fontWeight: 'bold',
                        // fontSize: '1.2em'
                    },
                    // '& .MuiDataGrid-row' : {
                    //     p : 2,
                    //     whiteSpace : 'normal'
                    // },
                    '& .MuiDataGrid-cell a' : {
                        // m : 1,
                        // p : 1,
                        textDecoration : 'none',
                        whiteSpace : 'normal'
                    },
                }}
                columns={[
                    {
                        field: 'serial', headerName: t('campaign.serial'), flex: 0.2, minWidth: 100, sortable : false, align: 'center', headerAlign: 'center'
                    },
                    {
                        field: 'name', headerName: t('campaign.name'), flex: 1, minWidth: 300, renderCell: (params) => {
                            return <Link to={`/campwiz/campaign/${params.row.id}`}>{params.value}</Link>
                        }
                        ,
                        align: 'center', headerAlign: 'center', pinnable : true
                    },
                    { align: 'center',headerAlign: 'center', field: 'language', headerName: t('campaign.language'), minWidth: 100, hideSortIcons: true, flex: 1 },
                    { align: 'center',headerAlign: 'center', field: 'start_at', headerName: t('campaign.startDate'), minWidth: 200, flex: 1 },
                    { align: 'center',headerAlign: 'center', field: 'end_at', headerName: t('campaign.endDate'), minWidth: 200, flex: 1 },
                    // {
                    //     field: 'actions', headerName: 'Actions', flex: 1, renderCell: (params) => {
                    //         return <Box sx={{
                    //             display: 'block',
                    //             // flexDirection: 'row',
                    //             // justifyContent: 'center',
                    //             // alignItems: 'center',
                    //             // gap: '1px'
                    //         }}>

                    //             <Button variant="contained" color="primary" size="small" sx={{
                    //                 padding: 1,
                    //                 m: 1
                    //             }}
                    //                 component={Link}
                    //                 to={`/campwiz/campaign/${params.row.id}/submission/new`}
                    //             >
                    //                 <AddIcon />
                    //             </Button>
                    //             <Button variant="contained" color="primary" size="small" sx={{
                    //                 padding: 1,
                    //                 m: 1
                    //             }}
                    //                 component={Link}
                    //                 to={`/campwiz/campaign/${params.row.id}/submission`}
                    //             >
                    //                 <GavelIcon />
                    //             </Button>
                    //             <Button variant="contained" color="primary" size="small" sx={{
                    //                 padding: 1,
                    //                 m: 1
                    //             }}
                    //                 component={Link}
                    //                 to={`/campwiz/campaign/${params.row.id}`}
                    //             >
                    //                 <CampaignIcon />
                    //             </Button>
                    //         </Box>
                    //     }
                    // },
                    { align: 'center', headerAlign: 'center', field: 'status', headerName: t('campaign.status'), flex: 0.5, minWidth: 150 },


                ]}
            />
        </div>
    )
}
export default CampaignList;
