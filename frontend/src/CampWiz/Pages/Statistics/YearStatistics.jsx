import Statistics from "./Statistics";
import { Link } from "react-router-dom";

import i18n from "../../../i18n";
const t = i18n.t;
const column2 = [
  { field: 'color', headerName: t('campaign.statistics.color'), align: 'center', headerAlign: 'center', minWidth: 70, sortable: false, renderCell: (params) => <span style={{ backgroundColor: params.value, width: '100%', height: '100%' }}></span> },
  { align: 'center', headerAlign: 'center', field: 'language', headerName: t('campaign.language'), sortable: false, minWidth: 100, flex: 1 },
  {
    align: 'center', headerAlign: 'center', field: 'name', headerName: t('campaign.name'), sortable: false, minWidth: 300, flex: 1, renderCell: (params) => {
      const campaignID = params.row.id;
      const campaignName = params.value;
      return <Link to={`/campwiz/statistics/${campaignID}`} component='a'>{campaignName}</Link>
    }
  },
  { align: 'center', headerAlign: 'center', field: 'start_at', headerName: t('campaign.startDate'), sortable: false, minWidth: 100, flex: 1 },
  { align: 'center', headerAlign: 'center', field: 'end_at', headerName: t('campaign.endDate'), sortable: false, minWidth: 100, flex: 1 },
  { align: 'center', headerAlign: 'center', field: 'status', headerName: t('campaign.status'), sortable: false, minWidth: 100, flex: 1 },
  { align: 'center', headerAlign: 'center', field: 'total_submissions', headerName: t('campaign.results.totalSubmission'), sortable: true, minWidth: 100, flex: 1 },
  { align: 'center', headerAlign: 'center', field: 'total_newly_created', headerName: t('campaign.results.totalNewlyCreated'), sortable: true, minWidth: 100, flex: 1 },
  { align: 'center', headerAlign: 'center', field: 'total_expanded', headerName: t('campaign.results.totalExpanded'), sortable: true, minWidth: 100, flex: 1 },
  { align: 'center', headerAlign: 'center', field: 'total_points', headerName: t('campaign.results.totalPoints'), sortable: true, minWidth: 100, flex: 1, renderCell: (params) => params.value / 10 },
]

const YearStatistics = () => {
  return <Statistics
    columns={column2}
    groupBy='language'
    title={t('campaign.statistics.title', { context: 'year' })}
  />
}
export default YearStatistics;
