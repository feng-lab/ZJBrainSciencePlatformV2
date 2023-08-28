"""create tables

Revision ID: 01b5380e17fc
Create Date: 2023-05-06 11:15:44

"""
import sqlalchemy as sa

from alembic import op

revision = "01b5380e17fc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "device",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("brand", sa.String(length=255), nullable=False, comment="设备品牌"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="设备名称"),
        sa.Column("purpose", sa.String(length=255), nullable=False, comment="设备用途"),
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
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("username", sa.String(length=255), nullable=False, comment="用户名"),
        sa.Column("hashed_password", sa.String(length=255), nullable=False, comment="密码哈希"),
        sa.Column("staff_id", sa.String(length=255), nullable=False, comment="员工号"),
        sa.Column("last_login_time", sa.DateTime(), nullable=True, comment="上次登录时间"),
        sa.Column("last_logout_time", sa.DateTime(), nullable=True, comment="上次下线时间"),
        sa.Column("access_level", sa.Integer(), nullable=False, comment="权限级别"),
        sa.PrimaryKeyConstraint("id"),
        comment="用户",
    )
    op.create_index(op.f("ix_user_staff_id"), "user", ["staff_id"], unique=False)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=False)
    op.create_table(
        "experiment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="实验名称"),
        sa.Column("type", sa.Enum("SSVEP", "MI", "neuron", "other", name="type"), nullable=False, comment="实验类型"),
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
        sa.ForeignKeyConstraint(["main_operator"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="实验",
    )
    op.create_index(op.f("ix_experiment_start_at"), "experiment", ["start_at"], unique=False)
    op.create_table(
        "human_subject",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="用户ID"),
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
        sa.Column("name", sa.String(length=50), nullable=True, comment="姓名"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="被试者",
    )
    op.create_index(op.f("ix_human_subject_user_id"), "human_subject", ["user_id"], unique=True)
    op.create_table(
        "notification",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("type", sa.Enum("task_step_status", name="type"), nullable=False, comment="消息类型"),
        sa.Column("creator", sa.Integer(), nullable=False, comment="消息发送者ID"),
        sa.Column("receiver", sa.Integer(), nullable=False, comment="消息接收者ID"),
        sa.Column("status", sa.Enum("unread", "read", name="status"), nullable=False, comment="消息状态"),
        sa.Column("content", sa.Text(), nullable=False, comment="消息内容"),
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
        "paradigm",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("creator", sa.Integer(), nullable=False, comment="创建者ID"),
        sa.Column("description", sa.Text(), nullable=False, comment="描述文字"),
        sa.ForeignKeyConstraint(["creator"], ["user.id"]),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="实验范式",
    )
    op.create_table(
        "file",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("paradigm_id", sa.Integer(), nullable=True, comment="范式ID，null表示不属于范式而属于实验"),
        sa.Column("name", sa.String(length=255), nullable=False, comment="逻辑路径"),
        sa.Column("extension", sa.String(length=50), nullable=False, comment="文件扩展名"),
        sa.Column("size", sa.Float(), nullable=False, comment="同一实验下的文件序号"),
        sa.Column("is_original", sa.Boolean(), nullable=False, comment="是否是设备产生的原始文件"),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.ForeignKeyConstraint(["paradigm_id"], ["paradigm.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="文件",
    )
    op.create_index(op.f("ix_file_experiment_id"), "file", ["experiment_id"], unique=False)
    op.create_index(op.f("ix_file_paradigm_id"), "file", ["paradigm_id"], unique=False)
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
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
        sa.ForeignKeyConstraint(["creator"], ["user.id"]),
        sa.ForeignKeyConstraint(["source_file"], ["file.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="任务",
    )
    op.create_table(
        "task_step",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键"),
        sa.Column("gmt_create", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="创建时间"),
        sa.Column("gmt_modified", sa.DateTime(), server_default=sa.text("now()"), nullable=False, comment="修改时间"),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False, comment="该行是否被删除"),
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
        sa.ForeignKeyConstraint(["task_id"], ["task.id"]),
        sa.ForeignKeyConstraint(["result_file_id"], ["file.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="任务步骤",
    )
    op.create_table(
        "experiment_tag",
        sa.Column("experiment_id", sa.Integer(), nullable=False, comment="实验ID"),
        sa.Column("tag", sa.String(length=50), nullable=False, comment="标签"),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiment.id"]),
        sa.PrimaryKeyConstraint("experiment_id", "tag"),
        comment="实验标签",
    )


def downgrade() -> None:
    op.drop_table("experiment_tag")
    op.drop_table("task_step")
    op.drop_table("task")
    op.drop_table("file")
    op.drop_table("paradigm")
    op.drop_table("experiment_human_subject")
    op.drop_table("experiment_device")
    op.drop_table("experiment_assistant")
    op.drop_table("notification")
    op.drop_table("human_subject")
    op.drop_table("experiment")
    op.drop_table("user")
    op.drop_table("human_subject_index")
    op.drop_table("device")
