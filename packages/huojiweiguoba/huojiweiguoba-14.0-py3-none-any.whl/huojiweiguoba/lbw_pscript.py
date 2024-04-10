import enum
import types
import pika
import time
import pickle
import os
from dotenv import find_dotenv, load_dotenv
from typing import Callable

from huojiweiguoba import lbw_datetime

env_path = find_dotenv(os.path.join(os.path.expanduser('~'), '.huojiweiguoba'))
assert env_path, "Not found .huojiweiguoba file"
load_dotenv(env_path)
assert os.getenv('RABBITMQ_HOST'), "RABBITMQ_HOST is None"
assert os.getenv('RABBITMQ_U'), "RABBITMQ_U is None"
assert os.getenv('RABBITMQ_P'), "RABBITMQ_P is None"
assert os.getenv('RABBITMQ_PORT'), "RABBITMQ_PORT is None"
assert os.getenv('RABBITMQ_QUEUENAME'), "RABBITMQ_QUEUENAME is None"


class ResultFormat(enum.Enum):
    basic = "基本格式"
    listing = "上新格式"


class ScriptType(enum.Enum):
    single = "单件装"
    multiple = "多件装"


class PsdTask:

    def __init__(self, stamp_list, template_list, script_type: ScriptType, result_format: ResultFormat, is_random=False,
                 random_num=10):
        self.script_type = script_type  # 脚本类型
        self.stamp_list = stamp_list  # 印花列表
        self.template_list = template_list  # 模板列表
        self.upload_time = lbw_datetime.get_local_now_date()  # 上传时间
        self.end_time = None  # 结束时间
        self.cost_time = None  # 耗时
        self.result_format: ResultFormat = result_format  # 结果格式
        self.is_random = is_random  # 是否随机组数
        self.random_num = random_num  # 随机组数


class RabbitMQ:
    def __init__(self, exchange):
        self.host = os.getenv('RABBITMQ_HOST')
        self.port = os.getenv('RABBITMQ_PORT')
        self.user = os.getenv('RABBITMQ_U')
        self.password = os.getenv('RABBITMQ_P')
        self.queue_name = os.getenv('RABBITMQ_QUEUENAME')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=pika.PlainCredentials(self.user, self.password),
                client_properties={'connection_name': exchange}
            )
        )
        self.channel = self.connection.channel()
        self.exchange = exchange

    def bind_queue(self):
        '''绑定队列'''
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def bind_exchange(self):
        '''绑定交换机'''
        self.channel.exchange_declare(
            exchange="1号伞兵卢本伟",
            exchange_type='direct',
            durable=True
        )
        self.channel.queue_bind(
            exchange="1号伞兵卢本伟",
            queue=self.queue_name
        )

    def publish(self, data: PsdTask):
        '''生产者'''
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        data = pickle.dumps(data)
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=data,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print("任务已发送")
        self.connection.close()

    def consume(self, func: Callable):
        '''消费者'''
        assert callable(func), f"Type of method_callback {type(func)} is not types.MethodType"

        def callback(ch, method, properties, body):
            '''
            收到消息的回调函数
            :param ch: ch代表信道
            :param method: method代表信道的方法
            :param properties: properties代表信道的属性
            :param body: body代表信道的内容
            :return:
            '''
            try:
                body = pickle.loads(body)
                assert isinstance(body, PsdTask), "body is not PsdTask..."
                run_result = func(body)
                print("run_result", run_result)
            except Exception as e:
                print("失败持久化")
            finally:
                # 手动标记消息已接收并处理完毕，RabbitMQ可以从queue中移除该条消息
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self.bind_queue()
        self.bind_exchange()
        self.channel.basic_qos(prefetch_count=1)  # prefetch_count=1 表示每次只接收一个
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=False  # auto_ack代表是否自动确认
        )
        print("等待任务处理中...")
        self.channel.start_consuming()
