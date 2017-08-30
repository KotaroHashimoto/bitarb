using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

using BitflyerApi;
using System.Net;

namespace bfCanceller
{

    public partial class Form1 : Form
    {

        String[] ss = new string[] {
                    "",
                    " ",
                    "  ",
                    "   ",
                    "    ",
                    "     ",
                    "      ",
                    "       ",
                    "        ",
                    "         "};

        bool mask = false;
        bool processing = false;
        BitflyerClient client = null;

        List<Order> orders = null;

        public Form1()
        {
            InitializeComponent();            
        }

        async Task getOpenOrders()
        {

            List<string> orderListA = new List<string>();
            List<string> orderListB = new List<string>();
            List<string> orderList = orderListA;

            listBox1.Items.Add("Connecting to BitFlyer server ...");


            while (true)
            {
                if (listBox1.DataSource != null)
                {
                    if (listBox1.DataSource.Equals(orderListA))
                    {
                        orderList = orderListB;
                    }
                    else
                    {
                        orderList = orderListA;
                    }
                }

                if(orderList != null)
                {
                    orderList.Clear();
                }

                try
                {
                    orders = await client.GetMyActiveOrders();
                }
                catch (Exception ex)
                {
                    listBox1.DataSource = null;
                    listBox1.Items.Add(ex);
                    listBox1.Items.Add("Connecting to BitFlyer server ...");

                    await Task.Delay(1000);
                    continue;
                }

                if (orders == null)
                {
                    orderList.Add("No Open Order.");
                }
                else if(orders.Count == 0)
                {
                    orderList.Add("No Open Order.");
                }
                else
                {
                    foreach (Order oo in orders)
                    {
                        string side = oo.Side.ToString();
                        string[] amount = oo.OutstandingSize.ToString().Split('.');
                        string price = oo.Price.ToString();
                        string date = oo.Date.ToLongTimeString() + ss[1] + oo.Date.ToLongDateString();

                        orderList.Add(ss[5 - side.Length] + side + ss[5 - amount[0].Length] + amount[0].Length +
                            (amount.Length == 2 ? ("." + amount[1] + ss[8 - amount[1].Length]) : ss[9]) + " BTC at " +
                            ss[7 - price.Length] + price + ss[3] + date);
                    }
                }

                int foc = listBox1.SelectedIndex;
                int pos = listBox1.TopIndex;

                if (!mask)
                {
                    listBox1.DataSource = orderList;
                }

                listBox1.SelectedIndex = (foc < orders.Count) ? foc : 0;
                listBox1.TopIndex = (pos < orders.Count) ? pos : 0;

                await Task.Delay(1000);
            }
        }


        private void listBox1_MouseCaptureChanged(object sender, EventArgs e)
        {
            mask = !mask;
        }

        private void listBox1_MouseClick(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void listBox1_MouseUp(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private void listBox1_MouseDown(object sender, MouseEventArgs e)
        {
            mask = false;
        }

        private async void listBox1_MouseDoubleClick(object sender, MouseEventArgs e)
        {

            if (!processing && orders != null)
            {
                processing = true;

                try
                {
                    if (listBox1.SelectedIndex < orders.Count) {
                        await client.CancelOrder(orders.ElementAt(listBox1.SelectedIndex));
                    }
                }
                catch (Exception ex)
                {
                    listBox1.DataSource = null;
                    listBox1.Items.Add(ex);
                    listBox1.Items.Add("Failed to cancel order.");

                    await Task.Delay(1000);
                }

                processing = false;
            }
        }

        private async void Form1_Load(object sender, EventArgs e)
        {

            String line = null;
            String key = null;
            String secret = null;

            try { 
                System.IO.StreamReader file = new System.IO.StreamReader("C:\\apikey.txt");

                while ((line = file.ReadLine()) != null)
                {
                    if (key == null)
                    {
                        key = line;
                    }
                    else if (secret == null)
                    {
                        secret = line;
                    }
                    else
                    {
                        break;
                    }
                }

                file.Close();
            }
            catch(Exception ex)
            {
                listBox1.Items.Add(ex);
            }

            if (key != null && secret != null)
            {
                client = new BitflyerClient(key, secret, ProductCode.FX_BTC_JPY);
                await getOpenOrders();
            }
            else
            {
                listBox1.Items.Add("Failed to read API key.");
            }
        }

        private async void button1_Click(object sender, EventArgs e)
        {
            await client.CancelAllOrders();
        }
    }
}
