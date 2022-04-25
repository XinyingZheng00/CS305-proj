#ifndef CLICK_MULTI_SOCKET_HH
#define CLICK_MULTI_SOCKET_HH
#include <click/element.hh>
#include <click/string.hh>
#include <click/task.hh>
#include <click/notifier.hh>
#include <sys/un.h>
CLICK_DECLS

#define MAX_CONNECTION_NUM 128

class MultiSocket : public Element { public:

    MultiSocket() CLICK_COLD;
    ~MultiSocket() CLICK_COLD;

    const char *class_name() const	{ return "MultiSocket"; }
    const char *port_count() const	{ return "1/1"; }
    const char *processing() const	{ return "h/h"; }
    const char *flow_code() const		{ return "x/y"; }
    const char *flags() const		{ return "S3"; }

    virtual int configure(Vector<String> &conf, ErrorHandler *) CLICK_COLD;
    virtual int initialize(ErrorHandler *) CLICK_COLD;
    virtual void cleanup(CleanupStage) CLICK_COLD;

    void selected(int fd, int mask);
    void push(int port, Packet*);

    void close_fd(int fd);
    int write_packet(int fd, Packet* p);

private:
    int _listen_fd;	// socket descriptor
    int _client_fd[MAX_CONNECTION_NUM];	// connection descriptor of clients
    int _server_fd[MAX_CONNECTION_NUM];	// connection descriptor of servers
    int _connection_index[MAX_CONNECTION_NUM * 2]; // fd to connection index

    struct sockaddr_in _local;
    socklen_t _local_len;

    struct sockaddr_in _remote;
    socklen_t _remote_len;

    int _protocol;
    IPAddress _local_ip;
    uint16_t _local_port;
    IPAddress _remote_ip;
    uint16_t _remote_port;

    bool _timestamp;		// set the timestamp on received packets
    int _snaplen;			// maximum received packet length
    unsigned _headroom;
    bool _verbose;		// be verbose

    int initialize_socket_error(ErrorHandler *, const char *);
};

CLICK_ENDDECLS
#endif
