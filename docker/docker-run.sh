#!/bin/bash

# Docker运行脚本 - Web SSH Terminal
# 使用方法: ./docker-run.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="web-ssh-terminal"
IMAGE_NAME="web-ssh-terminal"
CONTAINER_NAME="web-ssh-terminal"
PORT="5555"
VOLUME_NAME="ssh_data"

# 帮助信息
show_help() {
    echo -e "${BLUE}Web SSH Terminal Docker 部署脚本${NC}"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build     构建Docker镜像"
    echo "  run       运行容器（默认）"
    echo "  stop      停止容器"
    echo "  restart   重启容器"
    echo "  logs      查看容器日志"
    echo "  clean     清理容器和镜像"
    echo "  status    查看容器状态"
    echo "  shell     进入容器shell"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 build    # 构建镜像"
    echo "  $0 run      # 运行容器"
    echo "  $0 logs     # 查看日志"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装或未在PATH中${NC}"
        echo "请先安装Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
}

# 构建镜像
build_image() {
    echo -e "${BLUE}正在构建Docker镜像...${NC}"
    docker build -t $IMAGE_NAME .
    echo -e "${GREEN}镜像构建完成！${NC}"
}

# 运行容器
run_container() {
    echo -e "${BLUE}正在启动容器...${NC}"
    
    # 检查容器是否已存在
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${YELLOW}容器已存在，正在重启...${NC}"
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
    fi
    
    # 创建数据卷（如果不存在）
    docker volume create $VOLUME_NAME 2>/dev/null || true
    
    # 运行容器
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:5555 \
        -v $VOLUME_NAME:/app/backend/instance \
        --restart unless-stopped \
        $IMAGE_NAME
    
    echo -e "${GREEN}容器启动成功！${NC}"
    echo -e "${BLUE}访问地址: http://localhost:$PORT${NC}"
    echo -e "${BLUE}容器名称: $CONTAINER_NAME${NC}"
}

# 停止容器
stop_container() {
    echo -e "${BLUE}正在停止容器...${NC}"
    docker stop $CONTAINER_NAME 2>/dev/null || true
    echo -e "${GREEN}容器已停止${NC}"
}

# 重启容器
restart_container() {
    echo -e "${BLUE}正在重启容器...${NC}"
    docker restart $CONTAINER_NAME
    echo -e "${GREEN}容器重启完成${NC}"
}

# 查看日志
show_logs() {
    echo -e "${BLUE}容器日志（按Ctrl+C退出）:${NC}"
    docker logs -f $CONTAINER_NAME
}

# 清理资源
clean_resources() {
    echo -e "${YELLOW}警告: 这将删除容器、镜像和数据卷${NC}"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}正在清理资源...${NC}"
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        docker rmi $IMAGE_NAME 2>/dev/null || true
        docker volume rm $VOLUME_NAME 2>/dev/null || true
        echo -e "${GREEN}清理完成${NC}"
    else
        echo -e "${BLUE}取消清理${NC}"
    fi
}

# 查看状态
show_status() {
    echo -e "${BLUE}=== 容器状态 ===${NC}"
    if docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "^${CONTAINER_NAME}"; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -1
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "^${CONTAINER_NAME}"
        echo -e "${GREEN}容器正在运行${NC}"
    else
        echo -e "${YELLOW}容器未运行${NC}"
    fi
    
    echo -e "\n${BLUE}=== 镜像信息 ===${NC}"
    if docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -q "^${IMAGE_NAME}"; then
        docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -1
        docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep "^${IMAGE_NAME}"
    else
        echo -e "${YELLOW}镜像不存在${NC}"
    fi
    
    echo -e "\n${BLUE}=== 数据卷信息 ===${NC}"
    if docker volume ls --format "table {{.Name}}\t{{.Driver}}" | grep -q "${VOLUME_NAME}"; then
        docker volume ls --format "table {{.Name}}\t{{.Driver}}" | head -1
        docker volume ls --format "table {{.Name}}\t{{.Driver}}" | grep "${VOLUME_NAME}"
    else
        echo -e "${YELLOW}数据卷不存在${NC}"
    fi
}

# 进入容器shell
enter_shell() {
    echo -e "${BLUE}进入容器shell...${NC}"
    docker exec -it $CONTAINER_NAME /bin/bash
}

# 主程序
main() {
    check_docker
    
    case "${1:-run}" in
        "build")
            build_image
            ;;
        "run")
            build_image
            run_container
            ;;
        "stop")
            stop_container
            ;;
        "restart")
            restart_container
            ;;
        "logs")
            show_logs
            ;;
        "clean")
            clean_resources
            ;;
        "status")
            show_status
            ;;
        "shell")
            enter_shell
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}错误: 未知选项 '$1'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@" 