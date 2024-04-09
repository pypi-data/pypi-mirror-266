from src.core_pro import Drive


# url = '1vrcncbs1YGy9rWLBG3s35-mGpcUB8-A7'
# url = '1SU-YjuibMc1xO4KzDdVTSlODhLHrFXlx'
# a = Drive().get_file_info(url)

path = '/home/kevin/Downloads/1.csv'
folder_id = '1Ez8dNFmLQp936xkQlr1Ke1xW1WgJcvzD'
drive = Drive()
file_id = drive.upload(path, 'test.jpg', folder_id=folder_id)
drive.share_file(file_id, email='xuankhang.do@shopee.com')
