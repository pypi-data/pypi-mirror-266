from ipulse_shared_core_ftredge import UserProfile,  UserAuth
import datetime
import logging
logging.basicConfig(level=logging.INFO)
ex=UserProfile(uid="uid",
                organizations_uids={"20231220retailcustomer_coreorgn"},
                email="email@gmail.com",
                creat_date= datetime.datetime.now(datetime.UTC),
                creat_by_user='creat_by_user',
                updt_date=datetime.datetime.now(datetime.UTC),
                updt_by_user="subscriber_cf_persistUserAuthToUserProfile",
                approved=True,
                provider_id='provider_id',
                username='username')


logging.info(ex.model_dump(exclude_unset=True))