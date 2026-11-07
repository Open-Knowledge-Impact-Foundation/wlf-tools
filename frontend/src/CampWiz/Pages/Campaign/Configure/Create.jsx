import { useCallback, useState } from "react"
import EditableCampaign from "./EditableCampaign"
import CampWizServer from "../../../Server";
import ErrorPage from "../../../Components/ErrorPage";
import { useTranslation } from "react-i18next";

const CampaignCreate = () => {
    const { t } = useTranslation();
    const [error, setError] = useState(null);
    const handleSave = useCallback(async (campaign, setLoading) => {
        setLoading(true);
        try {
            const newCampaign = await CampWizServer.Campaign.createCampaign(campaign);
            const url = new URL("/campwiz/campaign/" + newCampaign.id, window.location.origin);
            setLoading(false);
            document.location.href = url;
            setError(null);
        } catch (e) {
            console.error(e);
            setError(e.message);
            setLoading(false);
        }
    }, [])
    return (
        <div>
            <h1>{t('campaign.action.create', { context: 'title' })}</h1>
            <EditableCampaign error={error} minimumStep={0} linear={true} defaultStep={0} showActions={false} onSave={handleSave} initialEditablity={false} />

        </div>
    )
}
export default CampaignCreate