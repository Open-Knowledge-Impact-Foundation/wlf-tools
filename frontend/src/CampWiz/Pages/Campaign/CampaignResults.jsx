import { DataGrid, GridToolbarColumnsButton, GridToolbarDensitySelector, GridToolbarExport, GridToolbarContainer, GridToolbarFilt, GridToolbarContainererButton, GridToolbarFilterButton } from "@mui/x-data-grid";
import { useEffect, useState } from "react";
import Typography from "@mui/material/Typography";
import CampWizServer from "../../Server";
import { Box } from "@mui/material";
import i18n from "../../../i18n";
const t = i18n.t;

const columns = [
    { field: 'username', headerName: t('campaign.results.username'), minWidth: 100, flex: 1 },
    { field: 'total_submissions', headerName: t('campaign.results.totalSubmission'), minWidth: 100, flex: 1 },
    { field: 'total_newly_created', headerName: t('campaign.results.totalNewlyCreated'), minWidth: 100, flex: 1 },
    { field: 'total_expanded', headerName:t('campaign.results.totalExpanded') , minWidth: 100, flex: 1 },
    // { field: 'total_negative_votes', headerName: 'Negative Votes', minWidth: 100, flex: 1 },
    { field: 'total_points', headerName: t('campaign.results.totalPoints'), minWidth: 100, flex: 1 , renderCell: (params) => params.value / 10 },
];
function CustomToolbar() {
    return (
      <GridToolbarContainer style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center' }}>
        <GridToolbarFilterButton />
        <GridToolbarExport />
      </GridToolbarContainer>
    );
  }
  
const CampaignResults = ({ campaign }) => {
    const [loading, setLoading] = useState(true);
    const [results, setResults] = useState(null);
    useEffect(() => {
        (async () => {
            setLoading(true);
            const results = await CampWizServer.Campaign.getResults(campaign.id);
            setResults(results);
            setLoading(false);
        })();
    }, [campaign]);
    return (
        <div>
            <Typography variant='h5' sx={{ textAlign: 'center', m: 2 }}>{t('campaign.results.title')}</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', gap: '1px', p: 1, m: 1, flexWrap: 'wrap' }}>
                <Typography variant='body1' sx={{ textAlign: 'center', m: 1 }}>{t('campaign.results.totalSubmission', {context : 'grand'})}: {results?.total_submissions}</Typography>
                <Typography variant='body1' sx={{ textAlign: 'center', m: 1 }}>{t('campaign.results.totalNewlyCreated', {context : 'grand'})}: {results?.total_newly_created}</Typography>
                <Typography variant='body1' sx={{ textAlign: 'center', m: 1 }}>{t('campaign.results.totalExpanded', {context : 'grand'})}: {results?.total_expanded}</Typography>
                <Typography variant='body1' sx={{ textAlign: 'center', m: 1 }}>{t('campaign.results.totalPoints', {context : 'grand'})}: {results?.total_points / 10}</Typography>
            </Box>
            <DataGrid
                loading={loading}
                rows={results?.submissions || []}
                autoHeight
                disableColumnMenu
                columns={columns}
                checkboxSelection={false}
                disableSelectionOnClick
                density="compact"
                hideFooterSelectedRowCount
                getRowId={row => row.username}
                slots={
                    {
                        toolbar: CustomToolbar,
                    }
                }
            />
        </div>
    )
}
export default CampaignResults;