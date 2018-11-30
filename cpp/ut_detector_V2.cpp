#include <iostream>
#include <thread>
#include <list>
#include <memory>
#include <fstream>
#include <errno.h>
#include <string.h>
#include "cuda_runtime_api.h"
#include "opencv2/opencv.hpp"
#include <unistd.h>
#include <sstream>
#include "zfz_timer.hpp"
#include "zfz_semphore.hpp"
#include "zfz_event.hpp"
#include "vega_face_interface.h"

using namespace std;
using namespace cv;

int batch_count = 1;
int batch_size = 1;

int finished_count = 0;
std::mutex finished_lock;
zfz::Event finished_event;

std::vector<std::vector<VegaFaceRect>> all_rects;

void detect_callback(VegaFaceTask *task)
{

    if (task->task_id > (batch_count - 1) * batch_size)
    {
        std::vector<VegaFaceRect> rects;
        for (int i = 0; i < task->faces_size; ++i)
        {
            rects.push_back(task->faces[i].rect);
        }
        all_rects.push_back(std::move(rects));
    }
    std::cout << "task[" << task->task_id << "]: detect finished, face count " << task->faces_size << std::endl;
    delete task;

    finished_lock.lock();
    ++finished_count;
    if (finished_count >= batch_count * batch_size)
    {
        finished_event.set();
        finished_count = 0;
    }
    finished_lock.unlock();
}

//read image_list into vector
void load_names(const std::string &name_list, std::vector<string> &names)
{
    std::ifstream fp(name_list);
    if (!fp)
    {
        std::cout << "Can't open list file " << name_list << std::endl;
        exit(-1);
    }
    names.resize(0); 
    std::string name;
    while (getline(fp, name))
    {
        names.push_back(name);
    }
}



int main(int argc, char** argv)
{
    
    VEGA_FACE_HANLE vega_face_handle = nullptr;

	//init vega_face and create instance
    int result = vega_face_create_instance("config.json", detect_callback, &vega_face_handle);
    if (result != VEGA_FACE_SUCCESS)
    {
        std::cout << "init vega face failed, error code " << result << std::endl;
        return 0;
    }
    
    int image_index = 0;
    int save_flag = 1;
    std::cout << "save flag " << save_flag << std::endl;

    all_rects.clear();
    std::string name_list = "/root/vega_cx_V2/vega/test/bin/vehicle_face.list";
    std::vector<string> names;
    load_names(name_list, names);
    int count = names.size();

    std::cout << "image count is :" << count << std::endl;
    
    std::vector<VegaFaceTask*> input_tasks(count);
    std::vector<cv::cuda::GpuMat> gpu_image(count);
    
    input_tasks.clear();
    gpu_image.clear();

    std::cout << "input_tasks.size: " << input_tasks.size() << " gpu_image.size: " << gpu_image.size() << std::endl;

    for(int i=0;i<count;i++)
    {
	std::cout << "start read image[" << i << "]: " << names[i] << std::endl;
        cv::Mat image = cv::imread(names[i]);
        if(image.data==0 & image.cols==0 & image.rows==0)
        {
            std::cout << "read image failed:" << " " << names[i] << std::endl;
            continue;    
        }

        gpu_image[i].upload(image);//Mat upload into GpuMat
           
        auto task = new VegaFaceTask();
        task->task_id = ++image_index;
        task->image.data = &gpu_image[i];
        task->image.width = 0;
        task->image.height = 0;
        task->image.format = VEGA_FACE_IMAGE_FORMAT_OPENCV_GPU_MAT;
        task->enable_detect = 1;
        task->enable_align = 0;
        task->enable_quality = 0;
        task->enable_feature = 0;
        task->enable_attribute = 0;
        input_tasks.push_back(task);
    }
	
    std::cout << "input_tasks_size is :" << input_tasks.size() << std::endl;
	//put tasks into queue
    int enqueue_result = vega_face_enqueue(vega_face_handle, &input_tasks[0], input_tasks.size());
    
    if (enqueue_result != VEGA_FACE_SUCCESS)
    {
    	std::cout << "vega face enqueue failed, error code " << enqueue_result << std::endl;
    	abort();
    }

    finished_event.wait();

    //std::cout << "gpu_image.col:" << gpu_image.cols << " " << "gpu_image.row:" << gpu_image.rows << " " << "gpu_image.channels:" << gpu_image.channels() << std::endl;

    input_tasks.clear();
    for (int i = 0; i < all_rects.size(); i++)
    {
	cv::Rect cv_rect;
	cv::Mat save_image;
	gpu_image[i].download(save_image);

	std::cout << "=========================start save image[" << i+1 << "]==========================" << std::endl;
	std::cout << "all_rects.size: " << all_rects[i].size() << std::endl;
	for (int j = 0; j < all_rects[i].size(); j++)
	{
	   auto &rect = all_rects[i][j];

	   cv_rect.x = rect.x;
	   cv_rect.y = rect.y;
	   cv_rect.width = rect.width;
	   cv_rect.height = rect.height;

	   std::cout <<  int(cv_rect.x) << " " << int(cv_rect.y) << " " << int(cv_rect.width) << " " << int(cv_rect.height) << " " << rect.confidence << std::endl;
	   std::ofstream rect_text;

	   std::string textName = names[i].substr (names[i].rfind("/")+1,names[i].size());
	   std::string txtName = textName.substr(0,textName.rfind("."));
	   rect_text.open("/root/vega_cx_V2/vega/test/bin/result_texts/vehicle_face/"+ txtName + ".txt",std::ios::out | std::ios::app);
	   
	   if(!rect_text.is_open())
	   {
	   	std::cout << "&&&&&&&&&&&&&&&&&&&&&&&&&&"<< std::endl;
	   	return 0;
	   }
	   rect_text << int(cv_rect.x) << " " << int(cv_rect.y) << " " << int(cv_rect.width) << " " << int(cv_rect.height) << " " << rect.confidence << std::endl;
	   rect_text.close();
	   cv::rectangle(save_image, cv_rect, cv::Scalar(255, 255, 0), 2);
    	}
        
        std::string save_name = names[i].substr(names[i].rfind("/")+1,names[i].size());
        cv::imwrite("/root/vega_cx_V2/vega/test/bin/result_photos/vehicle_face/"+save_name, save_image);
        std::cout<<"has done image: "<< " " << names[i] << std::endl;
	std::cout << "=========================end save image[" << i+1 << "]==========================" << std::endl;
	
    }

	for (int i = 0; i < all_rects.size(); i++)
	{
	    if(all_rects[i].empty())
	    {
	        std::cout << "not detect:" << " "  << names[i] << std::endl;
	        std::ofstream rect_no_det;
	        std::string no_det_Name = names[i].substr (names[i].rfind("/")+1,names[i].size());
	        std::string NO_det_Name = no_det_Name.substr(0,no_det_Name.rfind("."));
	        rect_no_det.open("/root/vega_cx_V2/vega/test/bin/result_texts/vehicle_face/" + NO_det_Name + ".txt",std::ios::out | std::ios::app);
	        std::cout << "*********************create blank txt*********************" << std::endl;
	        rect_no_det.close();
	        continue;
	    }
	}   

    vega_face_destroy_instance(vega_face_handle);
    vega_face_handle = nullptr;
    return 0;
}
