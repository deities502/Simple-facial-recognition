import pymysql
import numpy as np

def insert_face_data(id, name, face_descriptor):
    # 连接到数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='java',
        database='database_face',
        charset='utf8'
    )

    # 创建一个游标对象来执行SQL语句
    cursor = conn.cursor()

    # 创建表
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS  face (
        ID VARCHAR(255),
        NAME VARCHAR(255),
        FACEINFO TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    '''
    cursor.execute(create_table_query)

    # 插入数据
    insert_data_query = '''
    INSERT INTO face (ID, NAME, FACEINFO)
    VALUES (%s, %s, %s)
    '''
    try:
        # 执行sql语句
        cursor.execute(insert_data_query, (id, name, face_descriptor))
        # 提交到数据库执行
        conn.commit()
        print("数据插入成功")
    except:
        # 如果发生错误则回滚
        conn.rollback()
        print("数据插入失败")
    cursor.close()
    conn.close()


def insert_face(id, name, face_descriptor):
    # 连接到数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='java',
        database='database_face',
        charset='utf8'
    )

    # 创建一个游标对象来执行SQL语句
    cursor = conn.cursor()

    # 创建表
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS  in_face (
        ID VARCHAR(255),
        NAME VARCHAR(255),
        FACEINFO TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    '''
    cursor.execute(create_table_query)

    # 插入数据
    insert_data_query = '''
    INSERT INTO in_face (ID, NAME, FACEINFO)
    VALUES (%s, %s, %s)
    '''
    try:
        # 执行sql语句
        cursor.execute(insert_data_query, (id, name, face_descriptor))
        # 提交到数据库执行
        conn.commit()
        print("数据插入成功")
    except:
        # 如果发生错误则回滚
        conn.rollback()
        print("数据插入失败")
    cursor.close()
    conn.close()


def fetch_data_from_database():
    # 连接到数据库，并设置编码格式为utf8
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='java',
        database='database_face',
        charset='utf8'
    )

    # 创建一个游标对象来执行SQL语句
    cursor = conn.cursor()
    #
    # try:

    # 执行查询
    query = "SELECT ID, NAME, FACEINFO FROM face"
    cursor.execute(query)

    # 初始化列表
    id_list = []
    name_list = []
    feature_list = None

    # 逐行读取数据并存储到列表
    for row in cursor.fetchall():
        print(row)
        id_list.append(row[0])
        name_list.append(row[1])
        face_descriptor = row[2]
        face_descriptor = face_descriptor[1:-1].split()
        # 把列表转换array类型
        face_descriptor = list(face_descriptor)



        if feature_list is None:
            feature_list = face_descriptor

        else:
            feature_list = np.concatenate((feature_list, face_descriptor), axis=0)
    # 关闭游标和连接
    cursor.close()
    conn.close()

    # 返回结果列表
    return id_list, name_list, feature_list

    # except Exception as e:
    #     # 输出错误信息
    #     print("Failed to fetch data from database:", str(e))
    #     # 关闭游标和连接（如果出现异常）
    #     cursor.close()
    #     conn.close()
    #     # 返回空列表或None，表示读取失败
    #     return [], [], []
s,t,y=fetch_data_from_database()
print(s)