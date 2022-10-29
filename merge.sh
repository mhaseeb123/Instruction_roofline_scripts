#!/bin/bash -le

# print usage
function usage() {
    echo "USAGE: merge.sh </path/to/extended_output>"
}

# if no input params
if [ -z "$1" ]; then 
    usage
    exit -1
fi

# extended_output path
OPATH=${1}

# list of kernels
kernels=(SpSpGEMM)

# list of metrics
metric=(smsp__inst_executed.avg.per_cycle_active smsp__inst_executed.sum smsp__sass_thread_inst_executed_op_integer_pred_on.sum smsp__sass_thread_inst_executed_op_memory_pred_on.sum smsp__inst_executed_op_global_st.sum smsp__inst_executed_op_local_ld.sum smsp__inst_executed_op_local_st.sum smsp__inst_executed_op_shared_ld_pred_on_any.sum smsp__inst_executed_op_shared_st_pred_on_any.sum smsp__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_active smsp__sass_thread_inst_executed_op_conversion_pred_on.sum smsp__sass_thread_inst_executed_op_control_pred_on.sum smsp__sass_thread_inst_executed_op_fp64_pred_on.sum smsp__sass_thread_inst_executed_op_fp32_pred_on.sum smsp__sass_thread_inst_executed_op_fp16_pred_on.sum smsp__sass_thread_inst_executed_op_dadd_pred_on.sum smsp__sass_thread_inst_executed_op_dmul_pred_on.sum smsp__sass_thread_inst_executed_op_dfma_pred_on.sum smsp__sass_thread_inst_executed_op_fadd_pred_on.sum smsp__sass_thread_inst_executed_op_fmul_pred_on.sum smsp__sass_thread_inst_executed_op_ffma_pred_on.sum  smsp__sass_thread_inst_executed_op_hadd_pred_on.sum smsp__sass_thread_inst_executed_op_hmul_pred_on.sum smsp__sass_thread_inst_executed_op_hfma_pred_on.sum l1tex__t_sectors_pipe_lsu_mem_local_op_ld.sum l1tex__t_sectors_pipe_lsu_mem_local_op_st.sum l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum l1tex__average_t_sectors_per_request_pipe_lsu_mem_local_op_ld.ratio l1tex__average_t_sectors_per_request_pipe_lsu_mem_local_op_st.ratio l1tex__average_t_sectors_per_request_pipe_lsu_mem_global_op_ld.ratio l1tex__average_t_sectors_per_request_pipe_lsu_mem_global_op_st.ratio smsp__inst_executed_op_global_red.sum smsp__inst_executed_op_global_ld.sum  lts__t_sectors_op_write.sum lts__t_sectors_op_read.sum lts__t_sectors_op_atom.sum lts__t_sectors_op_red.sum dram__sectors_read.sum dram__sectors_write.sum lts__t_sectors_aperture_sysmem_op_read.sum lts__t_sectors_aperture_sysmem_op_write.sum smsp__sass_average_branch_targets_threads_uniform.pct smsp__thread_inst_executed_per_inst_executed.pct smsp__thread_inst_executed_per_inst_executed.ratio) 

# list of events
event=(sm__inst_executed.sum smsp__thread_inst_executed.sum)

# extract and append all of them in one file
for kernel in ${kernels[@]}
do
	echo ${kernel}
	filename="${OPATH}/${kernel}"
	echo ${filename}

	# remove previous file if exists
	rm -rf ${filename}

	# write all metrics
	for m in ${metric[@]}
	do
		echo $m
		data=`grep -rin -E "${kernel}.*\"${m}\"" ${OPATH}/${kernel}_*.log | awk -F'",' '{print $NF}' | sed 's/,//g' | sed 's/\"//g'`  
		echo "${m},${data}" >> ${filename}.csv
	done

	# write events
	for e in ${event[@]}
	do
		echo $e
		data=`grep -rin -E "${kernel}.*\"${e}\"" ${OPATH}/${kernel}_event.log | awk -F'",' '{print $NF}' | sed 's/,//g' | sed 's/\"//g'`  
		echo "${e},${data}" >> ${filename}.csv
	done

	# replace all spaces with comma to make a csv
	sed -i "s/,[[:blank:]]*$//g" ${filename}.csv

	# remove any trailing whitespaces
	sed -i 's/[[:blank:]]*$//' ${filename}.csv
done
