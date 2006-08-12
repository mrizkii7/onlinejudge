/********************************************************************************/
/*  题目：程序设计在线判断系统后台服务进程                                          */ 
/*  作者：温州大学计算机科学与工程学院 05届学生 吴宗大                               */
/*  运行环境：Debian Linux； 开发工具：ANSI C； DBMS：MySQL                        */
/*  完成日期：2005年5月1日                                                        */
/* compile command: gcc -lmysqlclient -lpthread Server0.c */

/********************************************************************************/

#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <netinet/in.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <mysql/mysql.h>
#include <syslog.h>

#define MYPORT 10001           //服务端口
#define MYIP   "localhost"     //服务器

typedef struct node
{
  pthread_t   thread_id;       //记录线程ID号
  pid_t       process_id;      //记录线程对应的执行程序的进程ID
  pid_t       shell_id;        //记录shell的ID
  unsigned    time_limit;      //算法题目的时间限制 
  unsigned    memory_limit;    //算法题目的内存限制
  char        userid[10];      //程序的提交用户
  char        problemid[10];   //执行程序对应的题目号
  struct node *next;             
} share_queue_node;            //共享队列结点结构

typedef struct
{
  share_queue_node *data;      //共享队列数据主体
  unsigned  length;            //共享队列长度
}share_queue_attr;

share_queue_attr squeue;        //定义服务进程中的共享队列squeue
           
pthread_mutex_t mutex_share_queue;
pthread_mutex_t mutex_queue_null;

int thread_exit_ok = 0;
int thread_exit_state = 1;

/*********************************************************************/
/*  主线程(Main Thread)：创建套接口(Socket)，监听Web的连接请求。               */
/*  当用户通过Web向后台服务进程发出连接请求时，主线程接受请求并产生一个处理线程来处 */
/*  理该连接，然后主线程继续监听。该线程在服务进程开启时被创建直到服务进程终止时撤消 */
/*********************************************************************/

int main()
{
   void disposal_pthread_function(void *);
   void monitor_pthread_function(void);
   
   int sock,* nsock;
   socklen_t sin_size;
   pthread_t thread;
   struct sockaddr_in my_addr,their_addr;

   system("rm -r tmpdir");
   system("mkdir tmpdir");
      
   if((sock=socket(AF_INET,SOCK_STREAM,0))==-1)
   {
       syslog(LOG_USER|LOG_INFO, "Socket Create Error\n");
       exit(1);
   }

   my_addr.sin_family=AF_INET;
   my_addr.sin_port=htons(MYPORT);
   my_addr.sin_addr.s_addr=inet_addr(MYIP);
   bzero(&(my_addr.sin_zero),8);

   if(bind(sock,(struct sockaddr *)&my_addr,sizeof(struct sockaddr))==-1)
   {
       syslog(LOG_USER|LOG_INFO, "Socket Bind Error");
       exit(1);
   }
      
   if(listen(sock,10)==-1)
   {
       syslog(LOG_USER|LOG_INFO, "Socket Listen Error");
       exit(1);
   }
   
   squeue.data=NULL;
   squeue.length=0;
   pthread_mutex_init(&mutex_share_queue,NULL);
   pthread_mutex_init(&mutex_queue_null,NULL);
   
   pthread_create(&thread, NULL,(void *)&monitor_pthread_function, NULL);
   
   sin_size=sizeof(struct sockaddr_in);
   while(1)
   {
       nsock=(int * )malloc(sizeof(int));
       if((*nsock=accept(sock,(struct sockaddr *)&their_addr,&sin_size))==-1)
       {
           syslog(LOG_USER|LOG_INFO, "Socket Accept Error");
           continue;
       }
       pthread_create(&thread, NULL,(void*)&disposal_pthread_function, (void *)nsock);
   }

}

/***************************************************************************/
/*  监测线程(Monitor Thread)： 根据进程共享队列给定的运行中的处理线程和对应执行程序的    */
/*  相关信息，监测所有执行程序的运行情况。当有运行程序超出题目的要求限制（内存限制、         */
/*  时间限制等）时，则中断该执行进程和对应的处理线程，并把结果信息写入数据库。当共享         */
/*  队列为空时，该线程处于阻塞状态。它也是在服务进程开启时被创建，随进程终止而撤消。         */
/***************************************************************************/

void monitor_pthread_function(void)
{
   void get_only_fn(char *);
   MYSQL_RES * db_query(char *sql);
   share_queue_node * delete_queue_element(share_queue_node *);

   share_queue_node * p;
   FILE * stat_fp,* statm_fp;
   unsigned run_time,run_memory;
   char str[100];
	  
   while(1)
   {   
       pthread_mutex_lock(&mutex_queue_null);

       pthread_mutex_lock(&mutex_share_queue);
         for(p=squeue.data;p;)
         {   
             sprintf(str,"/proc/%d/statm",p->process_id);
             if(!(statm_fp=fopen(str,"r")))
             { 
                 p=delete_queue_element(p);      
                 continue; 
             }
             
             sprintf(str,"/proc/%d/stat",p->process_id);
             if(!(stat_fp=fopen(str,"r")))
             { 
                 p=delete_queue_element(p); 
                 fclose(statm_fp); 
                 continue;
             }   
             
             fscanf(statm_fp,"%s",str); 
             run_memory=atoi(str);
             
             fscanf(stat_fp,"%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s%*s");
             fscanf(stat_fp,"%s",str); 
             run_time=atoi(str); 
             fscanf(stat_fp,"%s",str); 
             run_time+=atoi(str);
             
             fclose(statm_fp);
             fclose(stat_fp);   
                 
             if(run_memory/50>=p->memory_limit) 
             { 
                 sprintf(str,"kill %d",p->process_id);
                 system(str);       
                 sprintf(str,"kill %d",p->shell_id);
                 system(str);                        
                 pthread_cancel(p->thread_id); 
                 sprintf(str,"insert into feedbacks(userid,problemid,backinfo,\
                             runtime,runmemory) values(%s,%s,'memory limit',%d,%d)",
                             p->userid,p->problemid,run_time/100,run_memory/50);
                 db_query(str);
                 
                 sprintf(str,"update users set totalsubmittimes=totalsubmittimes+1\
                              where userid=%s",p->userid);
                 db_query(str);

                 p=delete_queue_element(p);
                 continue;
             }
             else if(run_time/100>=p->time_limit) 
             {  
                 sprintf(str,"kill %d",p->process_id);
                 system(str);
                 sprintf(str,"kill %d",p->shell_id);
                 system(str); 
                 pthread_cancel(p->thread_id);
                 sprintf(str,"insert into feedbacks(userid,problemid,backinfo,\
                             runtime,runmemory) values(%s,%s,'time limit',%d,%d)",
                             p->userid,p->problemid,run_time/100,run_memory/50);
                 db_query(str);
 
                 sprintf(str,"update users set totalsubmittimes=totalsubmittimes+1\
                              where userid=%s",p->userid);
                 db_query(str);
                 
                 p=delete_queue_element(p);
                 continue;
             }
                
             p=p->next;   

         }        
       pthread_mutex_unlock(&mutex_share_queue); 
         
       if(squeue.length)  
           pthread_mutex_unlock(&mutex_queue_null);

   }  
}

/**************************************************************************/
/*  处理线程(Disposal Thread)：每个客户端用户对应一个处理线程。它接收用户通过Web传送  */
/*  过来的答题程序源代码等数据，编译源码生成执行程序()，把执行程序的ID以及处理线程的      */
/*  相关信息写入进程共享队列(Share Queue) 。处理线程连接数据库取得该题目的测试数据，    */
/*  喂入测试输入数据之后运行执行程序，在执行程序运行完毕之后，判断运行结果正误，并把       */
/*  结果信息写入数据库。                                                                   */
/**************************************************************************/

void disposal_pthread_function( void * sock)
{
   void get_only_fn(char *);
   MYSQL_RES * db_query(char *);
   pid_t get_child_pid(pid_t );
   int compare_result(char *,char *);
   share_queue_node * delete_queue_element(share_queue_node *);  
   
   int n,i,j;
   char source_code[5050];
   char userid[20];
   char problemid[20];
   char language[10];
   
   if((n=recv(*((int *)sock),source_code,5050,0))==-1)
   {
       syslog(LOG_USER|LOG_INFO, "Receive Data Error\n");
       pthread_exit(&thread_exit_state);
   } 
   source_code[n]=0;

   for(i=j=0;i<n;i++)
       if(source_code[i]!='@')
           userid[j++]=source_code[i];
       else break;        
   userid[j]=0;

   for(i++,j=0;i<n;i++)
       if(source_code[i]!='@')
           problemid[j++]=source_code[i];
       else break;
   problemid[j]=0;

   for(i++,j=0;i<n;i++)
       if(source_code[i]!='@')
           language[j++]=source_code[i];
       else break;
   language[j]=0;
  
   for(j=i+1;source_code[j];j++)
        if(source_code[j]=='\\'&&source_code[j+1]=='"')
            for(n=j;source_code[n];n++)
                source_code[n]=source_code[n+1];
  
   char source_fn[30];
   FILE * fp;

   get_only_fn(source_fn);  
    
   if(!strcmp(language,"c++") || !strcmp(language, "C++")) 
       strcat(source_fn,".cxx");
   else
       strcat(source_fn,".c"); 

   fp=fopen(source_fn,"w");     
   fprintf(fp,"%s\n",source_code+i+1);  
   fclose(fp);               
  
   char exe_fn[30];
   get_only_fn(exe_fn); 
   strcat(exe_fn,".out");
    
   char cmd[150];
   char sql[150];
   sprintf(cmd,"g++ %s -o %s",source_fn,exe_fn);
   system(cmd); 
   
   sprintf(cmd,"rm %s",source_fn);
   system(cmd);
   if(access(exe_fn,0)==-1) 
   {   
       sprintf(sql,"insert into feedbacks(userid,problemid,backinfo) values\
                    (%s,%s,'compile error')",userid,problemid);
       if(!db_query(sql))
           syslog(LOG_USER|LOG_INFO, "Insert Data Error\n");

       sprintf(sql,"update users set totalsubmittimes=totalsubmittimes+1\
                    where userid=%s",userid);
       if(!db_query(sql))
           syslog(LOG_USER|LOG_INFO, "Update Data Error\n");

       pthread_exit(&thread_exit_state);    
   }   

   MYSQL_ROW m_row;
   MYSQL_RES * m_res;
   sprintf(sql,"select * from problems where problemid=%s",problemid);
   if(!(m_res = db_query(sql))) 
   {
       syslog(LOG_USER|LOG_INFO, "Select Data Error\n");
       sprintf(cmd,"rm %s",exe_fn); 
       system(cmd);  
       pthread_exit(&thread_exit_state); 
   }

   if(!(m_row = mysql_fetch_row(m_res))) 
   {
       syslog(LOG_USER|LOG_INFO, "Have Not The Problem\n");
       sprintf(cmd,"rm %s",exe_fn); 
       system(cmd); 
       pthread_exit(&thread_exit_state);
   }
   
   unsigned time_limit;
   unsigned memory_limit;
   time_limit=atoi(m_row[3]);
   memory_limit=atoi(m_row[4]);        
   
   sprintf(sql,"select * from tests where problemid=%s",problemid);
   if(!(m_res = db_query(sql)))
   {
       syslog(LOG_USER|LOG_INFO, "Select Data Error\n");
       sprintf(cmd,"rm %s",exe_fn); 
       system(cmd);  
       pthread_exit(&thread_exit_state); 
   }

   char in_fn[30];
   char out_fn[30];

   get_only_fn(in_fn);   
   get_only_fn(out_fn);
   strcat(in_fn,".txt");   
   strcat(out_fn,".txt");   

   pid_t pid;
   char str[5000];
   FILE * in_fp;
   FILE * out_fp;
   int first_flag=0;
   share_queue_node * pre,* p;
   while(m_row=mysql_fetch_row(m_res)) 
   {   
       in_fp =fopen(in_fn,"w+");
       out_fp=fopen(out_fn,"w+"); 
       
       fprintf(in_fp,"%s",m_row[1]);
       rewind(in_fp);                
       sprintf(cmd,"./%s <%s >%s",exe_fn,in_fn,out_fn);
       
       if(pid=fork()) 
       {   
           if(!first_flag) 
           {  
               pre=p=(share_queue_node *)malloc(sizeof(share_queue_node));
               p->thread_id=pthread_self(); 
               p->time_limit=time_limit;        
               p->memory_limit=memory_limit;
               strcpy(p->problemid,problemid); 
               strcpy(p->userid,userid);
               p->next=NULL;             
               
               pthread_mutex_lock(&mutex_share_queue);
                 p->next=squeue.data;
                 squeue.data=p;
                 squeue.length++;          
               pthread_mutex_unlock(&mutex_share_queue);

               first_flag=1;
           } 
       }    
        
       if(!pid) execlp("/bin/sh","sh","-c",cmd,(char *)0);
       if(!pid) exit(0);
       
       pthread_mutex_lock(&mutex_share_queue);
         pre->shell_id=pid;
         pre->process_id=get_child_pid(pid);
         if(pre->process_id==0) 
             delete_queue_element(pre);
         else 
             pthread_mutex_unlock(&mutex_queue_null);
       pthread_mutex_unlock(&mutex_share_queue);       

       if(pre->process_id)
       {
           sprintf(str,"/proc/%d/status",pre->process_id);
           while(fp=fopen(str,"r"))  fclose(fp); 
       }

       rewind(out_fp);
       fgets(str,5000,out_fp);               
       if(!compare_result(m_row[2],str)) 
       {  
           sprintf(sql,"insert into feedbacks(userid,problemid,backinfo)\
                       values(%s,%s,'wrong answer')",userid,problemid);
           if(!db_query(sql))
           {
               syslog(LOG_USER|LOG_INFO, "Insert Data Error\n");
               sprintf(cmd,"rm %s",exe_fn); 
               system(cmd);  
               sprintf(cmd,"rm %s",in_fn);  
               system(cmd);
               sprintf(cmd,"rm %s",out_fn); 
               system(cmd);
               pthread_exit(&thread_exit_state);   
           }   
           sprintf(sql,"update users set totalsubmittimes=totalsubmittimes+1\
                    where userid=%s",userid);
           db_query(sql);

           fclose(in_fp);  
           fclose(out_fp);
           pthread_exit(0);
       }
       
       sprintf(sql,"insert into feedbacks(userid,problemid,backinfo)\
                   values(%s,%s,'OK')",userid,problemid);
       if(!db_query(sql))
       	   syslog(LOG_USER|LOG_INFO, "Insert Data Error\n"); 
           
       sprintf(sql,"update users set totalsubmittimes=totalsubmittimes+1,\
                    acceptsubmittimes=acceptsubmittimes+1 where userid=%s",userid);
       if(!db_query(sql))
           syslog(LOG_USER|LOG_INFO, "Update Data Error\n");
                    
       sprintf(cmd,"rm %s",exe_fn); 
       system(cmd);
       sprintf(cmd,"rm %s",in_fn);  
       system(cmd);
       sprintf(cmd,"rm %s",out_fn); 
       system(cmd);  
       pthread_exit(&thread_exit_ok);   
   }  

}

int compare_result(char *str1,char *str2)
{
   int m=0,n=0,mlen,nlen;
  
   mlen=strlen(str1);
   nlen=strlen(str2);
   while(m<mlen&&n<nlen)
   {
       if(str1[m]==' ') { m++; continue; }
       if(str2[n]==' ') { n++; continue; }

       if(str1[m]!=str2[n]) return 0;

        m++; n++;
   }

   for(;m<mlen;m++)
       if(str1[m]!=' ') return 0;

   for(;n<nlen;n++)
       if(str1[n]!=' ') return 0; 

   return 1; 
      
}

share_queue_node * delete_queue_element(share_queue_node * p)
{
   share_queue_node * pp;

   pp=squeue.data;
   if(pp==p)
   {
       squeue.data=squeue.data->next;
       squeue.length--;
       free(p);
       return squeue.data;
   }

   for(;pp->next!=p;pp=pp->next) ;

   pp->next=p->next;
   squeue.length--;
   free(p);

   return pp->next;
}

pid_t get_child_pid(pid_t pid)
{
   void get_only_fn(char *);

   FILE *fp,*proc_fp;
   char str[100],cmd[40],pid_str[10],fn[30];   
   int i,j,n;

   get_only_fn(fn); 
   strcat(fn,".txt");
   sprintf(cmd,"ps au >%s",fn);  
   system(cmd);   

   if(!(fp=fopen(fn,"r"))) 
   {
       sprintf(cmd,"rm %s",fn);  
       system(cmd);
  	   return 0;
   }
   
   if(!feof(fp)) 
   	   fgets(str,100,fp);

   while(!feof(fp)) 
   {               
   	   fgets(str,100,fp);             

       for(i=0,n=strlen(str);i<n;i++)
         	 if(str[i]!=' ') break;
       
       for(;i<n;i++)
           if(str[i]==' ') break;
       
       for(;i<n;i++)
       		 if(str[i]!=' ') break;

       for(j=0;i<n;i++,j++)  
           if(str[i]!=' ') pid_str[j]=str[i]; 
           else  break;


       pid_str[j]=0; 
       sprintf(cmd,"/proc/%s/stat",pid_str); 

       if(!(proc_fp=fopen(cmd,"r"))) 
           continue;      
       
       fscanf(proc_fp,"%*s%*s%*s");
       fscanf(proc_fp,"%s",str);
       fclose(proc_fp);

       if(pid==atoi(str)) 
       { 
           sprintf(cmd,"rm %s",fn); 
           system(cmd);  
           
           return atoi(pid_str);
       }   
   }   

   fclose(fp);
   
   sprintf(cmd,"rm %s",fn);  
   system(cmd);   
   
   return 0;                 
} 

MYSQL_RES * db_query(char *sql)
{
   MYSQL mysql;             
   MYSQL_RES *m_res;      
   
   if( mysql_init(&mysql) == NULL ) 
   {
       syslog(LOG_USER|LOG_INFO,"Inital Mysql Handle Error\n");
       return NULL;
   } 

   if(mysql_real_connect(&mysql,"localhost","root","","acmbase",0,NULL,0) == NULL) 
   {   
       syslog(LOG_USER|LOG_INFO, "Failed To Connect To Database, Error: %s\n",
              mysql_error(&mysql));
       return NULL; 
   }  
   
   if(mysql_query(&mysql,sql)!= 0) 
   {  
       mysql_close(&mysql);      
       return NULL;  
   } 
   
   if(strstr("insert",sql)||strstr("update",sql)||strstr("delete",sql))
       return (MYSQL_RES *)0x0001;

   if(!(m_res = mysql_store_result(&mysql))) 
   { 
       mysql_close(&mysql);      
       return NULL;
   }
   
   return m_res;   
}

void get_only_fn(char *fn)
{ 
   int i,tmp;
   static char str[30]="tmpdir/000000000000000";

   for(i=strlen(str)-1;i>=0;i--)
   {
      tmp=str[i]-'0'+1;
      if(tmp<10)
      { str[i]=tmp+'0'; break; }
      else   str[i]='0';
   }
   
   strcpy(fn,str);
   return ;
}
