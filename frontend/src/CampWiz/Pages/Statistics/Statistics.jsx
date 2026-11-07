import React, { useEffect, useState } from 'react'
import { LineChart } from '@mui/x-charts/LineChart';
import CampWizServer from '../../Server';
import Card from "@mui/material/Card"
import CardHeader from "@mui/material/CardHeader"
import CardContent from "@mui/material/CardContent"
import Typography from "@mui/material/Typography"
import { DataGrid } from '@mui/x-data-grid';
import { useTranslation } from 'react-i18next';
import i18n from '../../../i18n';
import { CircularProgress } from '@mui/material';
export const generateRandomColor = () => '#' + Math.floor(Math.random() * 16777200 + 200).toString(16);
// shortest form with month as a abbreviation, no year, date is translated
const dateFormatter = {
  month: 'short',
  day: 'numeric',
}
const axis = [
  {
    dataKey: 'date',
    valueFormatter: (v) => new Date(v).toLocaleDateString(i18n.language, dateFormatter),
    type: 'category',
    scaleType: 'time',
    labelStyle: {
      fontSize: 14,
      transform: `translateY(${
        // Hack that should be added in the lib latter.
        5 * Math.abs(Math.sin((Math.PI * 45) / 180))
        }px)`
    },
    tickLabelStyle: {
      angle: 75,
      textAnchor: 'start',
      fontSize: 12,
    },
  },
];
const Statistics = ({ campaignID, columns, groupBy = 'language', title = 'User Submissions' }) => {
  const { t } = useTranslation();
  const [series, setSeries] = useState([]);
  const [rows, setRows] = useState([]);
  const [dataset, setDataset] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [overview, setOverview] = useState({
    total_submissions: 0,
    total_newly_created: 0,
    total_expanded: 0,
  });

  useEffect(() => {
    setLoading(true);
    const year = new Date().getFullYear();
    CampWizServer.Campaign.getTimeline(groupBy, campaignID, year).then((statistics) => {
      const { entities, timeline } = statistics;
      const overview = {
        total_submissions: statistics.total_submissions,
        total_newly_created: statistics.total_newly_created,
        total_expanded: statistics.total_expanded,
      };
      const series = [];
      for (const entityID in entities) {
        const entity = entities[entityID];
        series.push({
          dataKey: entityID,
          label: entity.name,
          valueFormatter: v => (v || 0),
          showMark: false,
          type: 'line',
          color: entity.color,
        });
      }
      setDataset(timeline);
      setSeries(series);
      setRows(Object.values(entities).sort((a, b) => {
        if (a.total_submissions !== b.total_submissions)
          return b.total_submissions - a.total_submissions;
        if (a.total_points !== b.total_points)
          return b.total_points - a.total_points;
        if (a.total_newly_created !== b.total_newly_created)
          return b.total_newly_created - a.total_newly_created;
        if (a.total_expanded !== b.total_expanded)
          return b.total_expanded - a.total_expanded;
        return b.name.localeCompare(a.name);
      }));
      setLoading(false);
      setOverview(overview);
      setError(null)
    }).catch((e) => {
      setError(e.message);
      setLoading(false);
    })
  }, [campaignID, groupBy]);
  return loading ? <CircularProgress /> : error ? <Typography variant='body1' color='error'>{error}</Typography> :
    <Card sx={{ p: 2 }}>
      <CardHeader title={title} />
      <CardContent sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
        mb: 2,
      }}>
        <Card component='fieldset' sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          justifyContent: 'center',
          p: 2,
          mb: 2,
          width: 'max-content',
          height: 'max-content',
        }}>
          <CardHeader title={t('campaign.statistics.overview')} component='legend' />
          <Typography variant='body1' component='label'>
            {t('campaign.results.totalSubmission', { context: 'grand', count: overview.total_submissions })} : {overview.total_submissions}
          </Typography>
          <Typography variant='body1' component='label'>
            {t('campaign.results.totalNewlyCreated', { context: 'grand', count: overview.total_newly_created })} : {overview.total_newly_created}
          </Typography>
          <Typography variant='body1' component='label'>
            {t('campaign.results.totalExpanded', { context: 'grand', count: overview.total_expanded })} : {overview.total_expanded}
          </Typography>
        </Card>
        <LineChart
          xAxis={axis}
          series={series}
          dataset={dataset}
          height={400}


          margin={{
            top: 50,
            right: 5,
            bottom: 50,
            left: 5,

          }}
          slotProps={{
            legend: {
              hidden: true,
            },
            lineHighlight: {

            },

          }}

        />

      </CardContent>
      <DataGrid
        loading={loading}
        rows={rows}
        autoHeight
        sx={{
          '& .MuiDataGrid-columnHeaderTitle': {
            fontWeight: 'bold',
            // fontSize: '1.2em'
          },
          // '& .MuiDataGrid-row' : {
          //     p : 2,
          //     whiteSpace : 'normal'
          // },
          '& .MuiDataGrid-cell a': {
            // m : 1,
            // p : 1,
            textDecoration: 'none',
            whiteSpace: 'normal'
          },
        }}
        disableColumnMenu
        columns={columns}
        checkboxSelection={false}
        disableSelectionOnClick
        density="compact"
        hideFooterSelectedRowCount
      />
    </Card>
}


export default Statistics
