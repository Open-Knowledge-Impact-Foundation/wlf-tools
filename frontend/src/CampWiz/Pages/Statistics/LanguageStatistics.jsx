import { useParams } from "react-router";
import Statistics from "./Statistics";
import { useTranslation } from "react-i18next";


const LanguageStatistics = () => {
  const { campaignID } = useParams();
  const { t } = useTranslation();
  const column = [
    { field: 'color', headerName: t('campaign.statistics.color'), align: 'center', headerAlign: 'center', minWidth: 50, sortable: false, flex: 0.5, renderCell: (params) => <span style={{ backgroundColor: params.value, width: '100%', height: '100%' }}></span> },
    { align: 'center', headerAlign: 'center', field: 'id', headerName: t('user.username'), sortable: false, minWidth: 100, flex: 1 },
    { align: 'center', headerAlign: 'center', field: 'total_submissions', headerName: t('campaign.results.totalSubmission'), sortable: true, minWidth: 100, flex: 1 },
    { align: 'center', headerAlign: 'center', field: 'total_newly_created', headerName: t('campaign.results.totalNewlyCreated'), sortable: true, minWidth: 100, flex: 1 },
    { align: 'center', headerAlign: 'center', field: 'total_expanded', headerName: t('campaign.results.totalExpanded'), sortable: true, minWidth: 100, flex: 1 },
    { align: 'center', headerAlign: 'center', field: 'total_points', headerName: t('campaign.results.totalPoints'), sortable: true, minWidth: 100, flex: 1 },
    
  ]
  return <Statistics
    campaignID={campaignID}
    columns={column}
    groupBy='user'
    title={t('campaign.statistics.title', { context: 'campaign' })}
  />

}
export default LanguageStatistics;
