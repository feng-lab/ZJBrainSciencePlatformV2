"""merge 20230925

Revision ID: 8dc0f8fefc93
Revises: 
Create Date: 2023-09-25 13:47:28.206356

"""
import sqlalchemy as sa

from alembic import op

revision = "8dc0f8fefc93"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "atlas",
        sa.Column("name", sa.String(length=255), nullable=False, comment="名称"),
        sa.Column("url", sa.String(length=255), nullable=False, comment="主页地址"),
        sa.Column("title", sa.String(length=255), nullable=False, comment="页面显示的标题"),
        sa.Column("whole_segment_id", sa.BigInteger(), nullable=True, comment="全脑轮廓ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱",
    )
    op.create_table(
        "atlas_behavioral_domain",
        sa.Column("name", sa.String(length=255), nullable=False, comment="名称"),
        sa.Column("value", sa.Double(), nullable=False, comment="值"),
        sa.Column("label", sa.String(length=255), nullable=False, comment="显示的名字"),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父节点ID，null表示第一层节点"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱的行为域结构数据，以树状结构存储",
    )
    op.create_table(
        "atlas_paradigm_class",
        sa.Column("name", sa.String(length=255), nullable=False, comment="名称"),
        sa.Column("value", sa.Double(), nullable=False, comment="值"),
        sa.Column("label", sa.String(length=255), nullable=False, comment="标签"),
        sa.Column("description", sa.Text(), nullable=False, comment="描述"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父节点ID，null表示第一层节点"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱范例集",
    )
    op.create_table(
        "atlas_region",
        sa.Column("region_id", sa.BigInteger(), nullable=True, comment="脑区ID"),
        sa.Column("description", sa.String(length=255), nullable=False, comment="描述"),
        sa.Column("acronym", sa.String(length=255), nullable=False, comment="缩写"),
        sa.Column("lobe", sa.String(length=255), nullable=True, comment="所属脑叶"),
        sa.Column("gyrus", sa.String(length=255), nullable=True, comment="所属脑回"),
        sa.Column("label", sa.String(length=255), nullable=True, comment="标签"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父节点ID，null表示第一层节点"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱脑区构成信息，以树状结构存储",
    )
    op.create_table(
        "atlas_region_behavioral_domain",
        sa.Column("key", sa.String(length=255), nullable=False, comment="行为域"),
        sa.Column("value", sa.Double(), nullable=False, comment="行为域值"),
        sa.Column("region_id", sa.BigInteger(), nullable=False, comment="脑区ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱中与脑区相关联的行为域数据",
    )
    op.create_table(
        "atlas_region_link",
        sa.Column("link_id", sa.Integer(), nullable=False, comment="连接信息ID"),
        sa.Column("region1", sa.String(length=255), nullable=False, comment="脑区1"),
        sa.Column("region2", sa.String(length=255), nullable=False, comment="脑区2"),
        sa.Column("value", sa.Double(), nullable=True, comment="连接强度，null表示仅有连接"),
        sa.Column("opposite_value", sa.Double(), nullable=True, comment="反向连接强度，null表示仅有连接"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱脑区之间的连接强度信息",
    )
    op.create_table(
        "atlas_region_paradigm_class",
        sa.Column("key", sa.String(length=255), nullable=False, comment="范例集"),
        sa.Column("value", sa.Double(), nullable=False, comment="范例集值"),
        sa.Column("region_id", sa.BigInteger(), nullable=False, comment="脑区ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("atlas_id", sa.Integer(), nullable=False, comment="所属图谱ID"),
        sa.PrimaryKeyConstraint("id"),
        comment="脑图谱中与脑区相关联的范例集",
    )
    op.create_table(
        "device",
        sa.Column("brand", sa.String(length=255), nullable=False, comment="设备品牌"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="设备名称"),
        sa.Column("purpose", sa.String(length=255), nullable=False, comment="设备用途"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.PrimaryKeyConstraint("id"),
        comment="实验设备",
    )
    op.create_table(
        "human_subject_index",
        sa.Column("index", sa.Integer(), nullable=False, comment="下一个被试者的序号"),
        sa.PrimaryKeyConstraint("index"),
        comment="被试者用户序号",
    )
    op.create_table(
        "user",
        sa.Column("username", sa.String(length=255), nullable=False, comment="用户名"),
        sa.Column("hashed_password", sa.String(length=255), nullable=False, comment="密码哈希"),
        sa.Column("staff_id", sa.String(length=255), nullable=False, comment="员工号"),
        sa.Column("last_login_time", sa.DateTime(), nullable=True, comment="上次登录时间"),
        sa.Column("last_logout_time", sa.DateTime(), nullable=True, comment="上次下线时间"),
        sa.Column("access_level", sa.Integer(), nullable=False, comment="权限级别"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.PrimaryKeyConstraint("id"),
        comment="用户",
    )
    op.create_index(op.f("ix_user_staff_id"), "user", ["staff_id"], unique=False)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=False)
    op.create_table(
        "experiment",
        sa.Column("name", sa.String(length=255), nullable=False, comment="实验名称"),
        sa.Column(
            "type", sa.Enum("other", "SSVEP", "MI", "neuron", name="experimenttype"), nullable=False, comment="实验类型"
        ),
        sa.Column("description", sa.Text(), nullable=False, comment="实验描述"),
        sa.Column("location", sa.String(length=255), nullable=False, comment="实验地点"),
        sa.Column("start_at", sa.DateTime(), nullable=False, comment="实验开始时间"),
        sa.Column("end_at", sa.DateTime(), nullable=False, comment="实验结束时间"),
        sa.Column("main_operator", sa.Integer(), nullable=False, comment="主操作者ID"),
        sa.Column("is_non_invasive", sa.Boolean(), nullable=True, comment="是否为无创实验"),
        sa.Column("subject_type", sa.String(length=50), nullable=True, comment="被试类型"),
        sa.Column("subject_num", sa.Integer(), nullable=True, comment="被试数量"),
        sa.Column("neuron_source", sa.String(length=50), nullable=True, comment="神经元细胞来源部位"),
        sa.Column("stimulation_type", sa.String(length=50), nullable=True, comment="刺激类型"),
        sa.Column("session_num", sa.Integer(), nullable=True, comment="实验session数量"),
        sa.Column("trail_num", sa.Integer(), nullable=True, comment="实验trail数量"),
        sa.Column("is_shared", sa.Boolean(), nullable=True, comment="实验是否公开"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["main_operator"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="实验",
    )
    op.create_index(op.f("ix_experiment_start_at"), "experiment", ["start_at"], unique=False)
    op.create_table(
        "human_subject",
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
        sa.Column("name", sa.String(length=50), nullable=True, comment="姓名"),
        sa.Column("gender", sa.Enum("male", "female", name="gender"), nullable=True, comment="性别"),
        sa.Column("birthdate", sa.Date(), nullable=True, comment="出生日期"),
        sa.Column("death_date", sa.Date(), nullable=True, comment="死亡日期"),
        sa.Column("education", sa.String(length=50), nullable=True, comment="教育程度"),
        sa.Column("occupation", sa.String(length=50), nullable=True, comment="职业"),
        sa.Column(
            "marital_status", sa.Enum("unmarried", "married", name="maritalstatus"), nullable=True, comment="婚姻状况"
        ),
        sa.Column("abo_blood_type", sa.Enum("A", "B", "AB", "O", name="abobloodtype"), nullable=True, comment="ABO血型"),
        sa.Column("is_left_handed", sa.Boolean(), nullable=True, comment="是否是左撇子"),
        sa.Column("phone_number", sa.String(length=50), nullable=True, comment="电话号码"),
        sa.Column("email", sa.String(length=100), nullable=True, comment="电子邮箱地址"),
        sa.Column("address", sa.String(length=255), nullable=True, comment="住址"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="被试者",
    )
    op.create_index(op.f("ix_human_subject_user_id"), "human_subject", ["user_id"], unique=True)
    op.create_table(
        "notification",
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("type", sa.Enum("task_step_status", name="notificationtype"), nullable=False, comment="消息类型"),
        sa.Column("creator", sa.Integer(), nullable=False, comment="消息发送者ID"),
        sa.Column("receiver", sa.Integer(), nullable=False, comment="消息接收者ID"),
        sa.Column("status", sa.Enum("unread", "read", name="notificationstatus"), nullable=False, comment="消息状态"),
        sa.Column("content", sa.Text(), nullable=False, comment="消息内容"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["creator"], ["user.id"]),
        sa.ForeignKeyConstraint(["receiver"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="通知",
    )
    op.create_index(op.f("ix_notification_gmt_create"), "notification", ["gmt_create"], unique=False)
    op.create_index(op.f("ix_notification_receiver"), "notification", ["receiver"], unique=False)
    op.create_table(
        "experiment_assistant",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("user_id", "experiment_id"),
        comment="实验助手关系",
    )
    op.create_table(
        "experiment_device",
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=False, comment="实验内序号"),
        sa.ForeignKeyConstraint(["device_id"], ["device.id"]),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.PrimaryKeyConstraint("experiment_id", "device_id"),
        comment="实验包含的设备",
    )
    op.create_table(
        "experiment_human_subject",
        sa.Column("experiment_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["human_subject.user_id"]),
        sa.PrimaryKeyConstraint("experiment_id", "user_id"),
        comment="实验包含的被试者",
    )
    op.create_table(
        "experiment_tag",
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("tag", sa.String(length=50), nullable=False, comment="标签"),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.PrimaryKeyConstraint("experiment_id", "tag"),
        comment="实验标签",
    )
    op.create_table(
        "paradigm",
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("creator", sa.Integer(), nullable=False, comment="创建者ID"),
        sa.Column("description", sa.Text(), nullable=False, comment="描述文字"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["creator"], ["user.id"]),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="实验范式",
    )
    op.create_table(
        "virtual_file",
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("paradigm_id", sa.Integer(), nullable=True, comment="范式ID，null表示不属于范式而属于实验"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="文件名"),
        sa.Column("file_type", sa.String(length=50), nullable=False, comment="文件类型"),
        sa.Column("is_original", sa.Boolean(), nullable=False, comment="是否是设备产生的原始文件"),
        sa.Column("size", sa.Float(), nullable=False, comment="显示给用户看的文件大小"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.ForeignKeyConstraint(["paradigm_id"], ["paradigm.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="虚拟文件",
    )
    op.create_index(op.f("ix_virtual_file_experiment_id"), "virtual_file", ["experiment_id"], unique=False)
    op.create_index(op.f("ix_virtual_file_paradigm_id"), "virtual_file", ["paradigm_id"], unique=False)
    op.create_table(
        "storage_file",
        sa.Column("virtual_file_id", sa.Integer(), nullable=False, comment="虚拟文件ID"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="文件名"),
        sa.Column("size", sa.Float(), nullable=False, comment="文件大小"),
        sa.Column("storage_path", sa.String(length=255), nullable=False, comment="文件系统存储路径"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["virtual_file_id"], ["virtual_file.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="实际文件",
    )
    op.create_index(op.f("ix_storage_file_virtual_file_id"), "storage_file", ["virtual_file_id"], unique=False)
    op.create_table(
        "task",
        sa.Column("name", sa.String(length=255), nullable=False, comment="任务名"),
        sa.Column("description", sa.Text(), nullable=False, comment="任务描述"),
        sa.Column("source_file", sa.Integer(), nullable=False, comment="任务分析的文件ID"),
        sa.Column(
            "type",
            sa.Enum("preprocess", "analysis", "preprocess_analysis", name="tasktype"),
            nullable=False,
            comment="任务类型",
        ),
        sa.Column("start_at", sa.DateTime(), nullable=True, comment="任务开始执行的时间"),
        sa.Column("end_at", sa.DateTime(), nullable=True, comment="任务结束时间"),
        sa.Column(
            "status",
            sa.Enum("wait_start", "running", "done", "error", "cancelled", name="taskstatus"),
            nullable=False,
            comment="任务状态",
        ),
        sa.Column("creator", sa.Integer(), nullable=False, comment="任务创建者ID"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["creator"], ["user.id"]),
        sa.ForeignKeyConstraint(["source_file"], ["virtual_file.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="任务",
    )
    op.create_table(
        "task_step",
        sa.Column("task_id", sa.Integer(), nullable=False, comment="任务ID"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="步骤名字"),
        sa.Column("type", sa.Enum("preprocess", "analysis", name="tasksteptype"), nullable=False, comment="任务步骤类型"),
        sa.Column("parameter", sa.Text(), nullable=False, comment="步骤参数JSON"),
        sa.Column("index", sa.Integer(), nullable=False, comment="任务中的步骤顺序"),
        sa.Column(
            "status",
            sa.Enum("wait_start", "running", "done", "error", "cancelled", name="taskstatus"),
            nullable=False,
            comment="步骤状态",
        ),
        sa.Column("start_at", sa.DateTime(), nullable=True, comment="步骤开始执行的时间"),
        sa.Column("end_at", sa.DateTime(), nullable=True, comment="步骤结束时间"),
        sa.Column("result_file_id", sa.Integer(), nullable=True, comment="结果文件ID"),
        sa.Column("error_msg", sa.String(length=255), nullable=True, comment="错误信息"),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.ForeignKeyConstraint(["result_file_id"], ["virtual_file.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="任务步骤",
    )


def downgrade() -> None:
    op.drop_table("task_step")
    op.drop_table("task")
    op.drop_index(op.f("ix_storage_file_virtual_file_id"), table_name="storage_file")
    op.drop_table("storage_file")
    op.drop_index(op.f("ix_virtual_file_paradigm_id"), table_name="virtual_file")
    op.drop_index(op.f("ix_virtual_file_experiment_id"), table_name="virtual_file")
    op.drop_table("virtual_file")
    op.drop_table("paradigm")
    op.drop_table("experiment_tag")
    op.drop_table("experiment_human_subject")
    op.drop_table("experiment_device")
    op.drop_table("experiment_assistant")
    op.drop_index(op.f("ix_notification_receiver"), table_name="notification")
    op.drop_index(op.f("ix_notification_gmt_create"), table_name="notification")
    op.drop_table("notification")
    op.drop_index(op.f("ix_human_subject_user_id"), table_name="human_subject")
    op.drop_table("human_subject")
    op.drop_index(op.f("ix_experiment_start_at"), table_name="experiment")
    op.drop_table("experiment")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_staff_id"), table_name="user")
    op.drop_table("user")
    op.drop_table("human_subject_index")
    op.drop_table("device")
    op.drop_table("atlas_region_paradigm_class")
    op.drop_table("atlas_region_link")
    op.drop_table("atlas_region_behavioral_domain")
    op.drop_table("atlas_region")
    op.drop_table("atlas_paradigm_class")
    op.drop_table("atlas_behavioral_domain")
    op.drop_table("atlas")
