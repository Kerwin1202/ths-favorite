#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from favorite import THSUserFavorite
from flask import Flask, request, jsonify, send_from_directory, make_response, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ths = None  # 全局变量

@app.route("/list_groups", methods=["GET"])
def list_groups():
    """列出所有分组及其股票数量"""
    groups = ths.get_all_groups()
    print(f"共有 {len(groups)} 个分组:")
    result = []
    for name, group in groups.items():
        result.append({
            "name": name,
            "group_id": group.group_id,
            "count": len(group.items)
        })
    return jsonify(result)

@app.route("/list_stocks", methods=["GET"])
def list_stocks():
    group_name = request.args.get("group")
    if not group_name:
        return jsonify({"error": "请传入参数 ?group=xxx"}), 400

    """列出指定分组中的所有股票"""
    groups = ths.get_all_groups()
    
    if group_name not in groups:
        print(f"未找到名为 '{group_name}' 的分组")
        return
    
    group = groups[group_name]
    print(f"分组 '{group_name}' (ID: {group.group_id}) 包含 {len(group.items)} 个股票:")
    
    result = []
    for item in group.items:
        # print(f"- {item.code}.{item.market}")
        result.append({
            "code": item.code,
            "market": item.market,
        })
    return jsonify(result)


@app.route("/add_stocks", methods=["GET"])
def add_stocks():
    group_name = request.args.get("group")
    stock_code = request.args.get("stock")
    
    if not group_name or not stock_code:
        return jsonify({"error": "请传入参数 ?group=xxx&stock=xxx"}), 400

    """添加股票到指定分组"""
    result = ths.add_item_to_group(group_name, stock_code)
    if result:
        print(f"已成功添加 {stock_code} 到分组 '{group_name}'")
        return jsonify({"message": f"已成功添加 {stock_code} 到分组 '{group_name}'"})
    else:
        return jsonify({"error": "添加失败"}), 500
    
@app.route("/delete_stocks", methods=["GET"])
def delete_stocks():
    group_name = request.args.get("group")
    stock_code = request.args.get("stock")
    
    if not group_name or not stock_code:
        return jsonify({"error": "请传入参数 ?group=xxx&stock=xxx"}), 400

    """从指定分组删除股票"""
    result = ths.delete_item_from_group(group_name, stock_code)
    if result:
        print(f"已成功从分组 '{group_name}' 删除 {stock_code}")
        return jsonify({"message": f"已成功从分组 '{group_name}' 删除 {stock_code}"})
    else:
        return jsonify({"error": "删除失败"}), 500
    
@app.route("/add_group", methods=["GET"])
def add_group():
    group_name = request.args.get("group")
    
    if not group_name:
        return jsonify({"error": "请传入参数 ?group=xxx"}), 400

    """添加新分组"""
    result = ths.add_group(group_name)
    if result:
        print(f"已成功添加分组 '{group_name}'")
        return jsonify({"message": f"已成功添加分组 '{group_name}'"})
    else:
        return jsonify({"error": "添加分组失败"}), 500
    
@app.route("/delete_group", methods=["GET"])
def delete_group():
    group_name = request.args.get("group")
    
    if not group_name:
        return jsonify({"error": "请传入参数 ?group=xxx"}), 400

    """删除指定分组"""
    result = ths.delete_group(group_name)
    if result:
        print(f"已成功删除分组 '{group_name}'")
        return jsonify({"message": f"已成功删除分组 '{group_name}'"})
    else:
        return jsonify({"error": "删除分组失败"}), 500

@app.route("/share_group", methods=["GET"])
def share_group():
    group_name = request.args.get("group")
    expire_time = request.args.get("time")
    
    if not group_name or not expire_time:
        return jsonify({"error": "请传入参数 ?group=xxx&time=xxx"}), 400

    """分享分组"""
    result = ths.share_group(group_name, expire_time)
    if result:
        print(f"已成功分享分组 '{group_name}'")
        return jsonify({"message": f"已成功分享分组 '{group_name}'"})
    else:
        return jsonify({"error": "分享分组失败"}), 500

def main():
    parser = argparse.ArgumentParser(description="同花顺自选股管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出分组")
    list_parser.add_argument("-g", "--group", help="指定分组名称，列出该分组中的股票")
    
    # add 命令
    add_parser = subparsers.add_parser("add", help="添加股票到分组")
    add_parser.add_argument("group", help="分组名称或ID")
    add_parser.add_argument("stock", help="股票代码，格式: code.market (如: 600519.SH)")
    
    # delete 命令
    del_parser = subparsers.add_parser("delete", help="从分组删除股票")
    del_parser.add_argument("group", help="分组名称或ID")
    del_parser.add_argument("stock", help="股票代码，格式: code.market (如: 600519.SH)")
    
    # add 命令
    add_group_parser = subparsers.add_parser("addgroup", help="添加分组")
    add_group_parser.add_argument("group", help="分组名称或ID")
    
    # delete 命令
    del_group_parser = subparsers.add_parser("deletegroup", help="删除分组")
    del_group_parser.add_argument("group", help="分组名称或ID")

    # share 命令
    share_parser = subparsers.add_parser("share", help="分享分组")
    share_parser.add_argument("group", help="分组名称或ID")
    share_parser.add_argument("time", help="多少毫秒后过期, 有效期 0 是永久")
    
    args = parser.parse_args()
    
    # 创建 THSUserGroups 实例
    with THSUserFavorite() as ths:
        # 处理命令
        if args.command == "list":
            if args.group:
                list_stocks(ths, args.group)
            else:
                list_groups(ths)
        elif args.command == "add":
            result = ths.add_item_to_group(args.group, args.stock)
            if result:
                print(f"已成功添加 {args.stock} 到分组 '{args.group}'")
        elif args.command == "delete":
            result = ths.delete_item_from_group(args.group, args.stock)
            if result:
                print(f"已成功从分组 '{args.group}' 删除 {args.stock}")
        elif args.command == "addgroup":
            result = ths.add_group(args.group)
            if result:
                print(f"已成功添加分组 '{args.group}'")
        elif args.command == "deletegroup":
            result = ths.delete_group(args.group)
            if result:
                print(f"已成功删除分组 '{args.group}'")
        elif args.command == "share":
            result = ths.share_group(args.group, args.time)
            if result:
                print(f"已成功分享分组 '{args.group}'")
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    #main()
    ths = THSUserFavorite()
    try:
        app.run(host="0.0.0.0", port=8166, debug=True)
    finally:
        print("🔌 已断开行情服务器")
